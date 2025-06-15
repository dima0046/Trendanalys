# myapp/telegram/tasks.py
import logging
import os
import asyncio
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types
from asgiref.sync import sync_to_async
from PIL import Image
from .models import TelegramChannel, TelegramPost, ParserLog
from .views import model, vectorizer, predict_category
from dotenv import load_dotenv

load_dotenv()
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

logger = logging.getLogger(__name__)

async def fetch_daily_telegram_data(channel, start_date, end_date):
    logger.info(f"API ID: {api_id}, API HASH: {api_hash}")
    client = TelegramClient('session_name', api_id, api_hash)
    try:
        logger.info(f"Подключение к Telegram для {channel.url}")
        await client.connect()
        if not await client.is_user_authorized():
            logger.error(f"Клиент не авторизован для {channel.url}")
            raise Exception("Клиент Telegram не авторизован. Требуется ручная авторизация.")

        entity = await client.get_entity(channel.url)
        channel.title = entity.title
        await sync_to_async(channel.save)()

        subscriber_count = 0
        try:
            full_channel = await client(functions.channels.GetFullChannelRequest(channel=entity))
            subscriber_count = int(getattr(full_channel.full_chat, 'participants_count', 0))
            logger.info(f"Подписчики для {channel.url}: {subscriber_count}")
        except Exception as e:
            logger.error(f"Ошибка получения количества подписчиков для {channel.url}: {str(e)}")

        avatar_dir = os.path.join('temp_data', 'avatars')
        os.makedirs(avatar_dir, exist_ok=True)
        avatar_filename = f"channel_{entity.id}.jpg"
        avatar_full_path = os.path.join(avatar_dir, avatar_filename)
        avatar_path = None
        if hasattr(entity, 'photo') and entity.photo:
            try:
                photo = await client.download_profile_photo(entity, file=avatar_full_path)
                if photo and os.path.exists(avatar_full_path):
                    with Image.open(avatar_full_path) as img:
                        img = img.resize((50, 50), Image.LANCZOS)
                        img.save(avatar_full_path, 'JPEG', quality=85)
                    avatar_path = f"avatars/{avatar_filename}"
                    logger.info(f"Аватар сохранен для {channel.url}")
            except Exception as e:
                logger.error(f"Ошибка загрузки аватара для {channel.url}: {str(e)}")

        total_engagement = 0
        total_comments = 0
        post_count = 0
        data = []
        combined_message = None

        logger.info(f"Начало парсинга постов для {channel.url} с {start_date} по {end_date}")
        async for post in client.iter_messages(entity, reverse=True, offset_date=end_date):
            post_date = timezone.make_aware(post.date, timezone=timezone.UTC)  # Правильный импорт UTC
            if post_date < start_date or (end_date and post_date > end_date):
                logger.debug(f"Пост {post.id} ({post_date}) вне диапазона {start_date} - {end_date}")
                continue

            logger.debug(f"Обрабатывается пост {post.id} от {post_date}")
            post_type = 'text'
            if post.media:
                if isinstance(post.media, types.MessageMediaPhoto):
                    post_type = 'image'
                elif isinstance(post.media, types.MessageMediaDocument) and post.media.document.mime_type.startswith('video'):
                    post_type = 'video'

            message_text = post.message if post.message else 'N/A'
            if message_text == 'N/A' and (not post.grouped_id or (combined_message and combined_message.get('post_id') != post.id)):
                if post.grouped_id and combined_message:
                    combined_message['message'] += f"\n[{post_type.capitalize()}: {post.id}]"
                    combined_message['link'] = f"https://t.me/{entity.username}/{post.id}"
                continue

            if post.media and isinstance(post.media, types.MessageMediaPhoto) and not post.message and combined_message and combined_message.get('message') != 'N/A':
                combined_message['message'] += f"\n[Изображение: {post.media.photo.id}]"
                combined_message['link'] = f"https://t.me/{entity.username}/{post.id}"
                continue

            comments_count = post.replies.replies if hasattr(post, 'replies') and post.replies else 0
            reactions_count = sum(reaction.count for reaction in post.reactions.results) if hasattr(post, 'reactions') and post.reactions else 0
            forwards_count = post.forwards if hasattr(post, 'forwards') else 0
            views = post.views if hasattr(post, 'views') else 0

            try:
                category = predict_category(message_text, model, vectorizer) if message_text != 'N/A' else 'N/A'
                logger.debug(f"Категория для поста {post.id}: {category}")
            except Exception as e:
                logger.error(f"Ошибка классификации для поста {post.id}: {str(e)}")
                category = 'N/A'

            post_engagement = reactions_count + forwards_count + comments_count
            total_engagement += post_engagement
            total_comments += comments_count
            post_count += 1

            er_post = (post_engagement / subscriber_count * 100) if subscriber_count > 0 and post_engagement > 0 else 0
            er_view = (post_engagement / views * 100) if views > 0 and post_engagement > 0 else 0
            vr_post = (views / subscriber_count * 100) if subscriber_count > 0 and views > 0 else 0

            post_data = {
                'channel': channel,
                'post_id': post.id,
                'date': post_date,
                'message': message_text,
                'link': f"https://t.me/{entity.username}/{post.id}" if entity.username else f"https://t.me/c/{entity.id}/{post.id}",
                'views': views,
                'reactions': reactions_count,
                'forwards': forwards_count,
                'comments_count': comments_count,
                'category': category,
                'avatar': avatar_path,
                'er_post': round(er_post, 2),
                'er_view': round(er_view, 2),
                'vr_post': round(vr_post, 2),
                'post_type': post_type,
                'subscribers': subscriber_count
            }
            data.append(post_data)

            try:
                with transaction.atomic():
                    obj, created = await sync_to_async(TelegramPost.objects.update_or_create)(
                        channel=channel,
                        post_id=post.id,
                        defaults={
                            'date': post_date,
                            'message': message_text,
                            'link': post_data['link'],
                            'views': views,
                            'reactions': reactions_count,
                            'forwards': forwards_count,
                            'comments_count': comments_count,
                            'category': category,
                            'avatar': avatar_path,
                            'er_post': round(er_post, 2),
                            'er_view': round(er_view, 2),
                            'vr_post': round(vr_post, 2),
                            'post_type': post_type,
                            'subscribers': subscriber_count
                        }
                    )
                    logger.info(f"Сохранен пост {post.id}, создан: {created}, дата: {post_date}")
            except Exception as e:
                logger.error(f"Ошибка сохранения поста {post.id} в транзакции: {str(e)}")

        tr = (total_comments / subscriber_count / post_count * 100) if post_count > 0 and subscriber_count > 0 else 0
        for item in data:
            item['tr'] = round(tr, 2)
        try:
            with transaction.atomic():
                await sync_to_async(TelegramPost.objects.filter(channel=channel).update)(tr=round(tr, 2))
                logger.info(f"Обновлен TR для канала {channel.url}: {tr}")
        except Exception as e:
            logger.error(f"Ошибка обновления TR для канала {channel.url}: {str(e)}")

        logger.info(f"Парсинг завершен, собрано {len(data)} постов для {channel.url}")
        return data
    except Exception as e:
        logger.error(f"Ошибка получения данных для канала {channel.url}: {str(e)}")
        raise
    finally:
        if client.is_connected():
            await client.disconnect()
            logger.info("Клиент отключен")

async def run_daily_parser_manual():
    logger.info("Запуск run_daily_parser_manual")
    channels = await sync_to_async(lambda: list(TelegramChannel.objects.filter(is_active=True)))()
    logger.info(f"Количество активных каналов: {len(channels)}")
    yesterday = timezone.now().date() - timedelta(days=1)  # 15 июня 2025
    start_date = timezone.make_aware(datetime.combine(yesterday, datetime.min.time()), timezone.get_current_timezone())
    end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    logger.info(f"Парсинг за период: {start_date} - {end_date}")

    for channel in channels:
        logger.info(f"Обработка канала: {channel.url}")
        log = await sync_to_async(ParserLog.objects.create)(channel=channel, status='RUNNING')
        try:
            data = await fetch_daily_telegram_data(channel, start_date, end_date)
            log.status = 'SUCCESS'
            log.posts_fetched = len(data)
            log.message = f"Обработка успешно завершена, получено {len(data)} постов."
            logger.info(f"Собрано {len(data)} постов для {channel.url}")
        except Exception as e:
            log.status = 'FAILED'
            log.message = str(e)
            logger.error(f"Ошибка для {channel.url}: {str(e)}")
        log.end_time = timezone.now()
        await sync_to_async(log.save)()

@shared_task
def run_daily_parser():
    logger.info("Запуск задачи run_daily_parser")
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(run_daily_parser_manual())
        logger.info("Задача run_daily_parser завершена успешно")
    except Exception as e:
        logger.error(f"Ошибка в run_daily_parser: {str(e)}")
        raise

print("tasks.py loaded")