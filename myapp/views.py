# Django imports
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator

# Forms
from .forms import TelegramForm

# Regular expressions
import re

# Date and time
from datetime import datetime, timezone
import time

# Telegram related imports
from telethon import TelegramClient
from telethon import utils
from telethon import types

# Logging
import logging

# Excel processing
import openpyxl

# JSON handling
import json

# UUID generation
import uuid

# Operating system utilities
import os

# Environment variables
from dotenv import load_dotenv

# Machine learning imports
from machine_learning.train_model import load_model, predict_category, update_model, get_unique_categories, export_model

load_dotenv()
api_id = os.getenv("API_ID")  
api_hash = os.getenv("API_HASH")  

# Загрузка модели и векторизатора при старте
model, vectorizer = load_model()

def cleanup_temp_data(folder='temp_data', max_age_seconds=86400):
    """
    Удаляет файлы в указанной папке, которые старше max_age_seconds.
    По умолчанию удаляет файлы старше одного дня (86400 секунд).
    """
    now = time.time()
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            file_age = now - os.path.getmtime(file_path)
            if file_age > max_age_seconds:
                os.remove(file_path)
                logging.debug(f"Deleted old file: {file_path}")

def extract_username(url):
    match = re.search(r'https://t.me/([^/?]+)', url)
    if match:
        return match.group(1)
    raise ValueError("Invalid Telegram URL")

async def fetch_telegram_data(channel_url, start_date=None, end_date=None):
    global model, vectorizer
    client = TelegramClient('session_name', api_id, api_hash)
    try:
        if not client.is_connected():
            await client.connect()
        if not await client.is_user_authorized():
            print("Please enter your phone number (e.g., +79991234567): ")
            phone = input().strip()
            await client.start(phone=phone)

        if start_date:
            start_date = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        if end_date:
            end_date = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)

        if "https://t.me/" in channel_url:
            username = channel_url.split('/')[-1]
        elif "https://web.telegram.org/k/#" in channel_url:
            channel_id = int(channel_url.split('#')[-1])
            username = utils.get_peer_id(types.PeerChannel(channel_id))
        else:
            username = extract_username(channel_url)

        entity = await client.get_entity(username)
        data = []
        combined_message = None

        async for post in client.iter_messages(entity, reverse=True, offset_date=start_date):
            if post.date > end_date:
                break

            if post.media and isinstance(post.media, types.MessageMediaPhoto) and not post.message:
                if combined_message:
                    combined_message['message'] += f"\n[Изображение: {post.media.photo.id}]"
                    combined_message['link'] = f"https://t.me/{entity.username}/{post.id}"
                continue

            comments_count = post.replies.replies if hasattr(post, 'replies') and post.replies else 0

            message_text = post.message if post.message else 'N/A'
            # Автоматическая категоризация с помощью модели
            category = predict_category(message_text, model, vectorizer)

            combined_message = {
                'title': entity.title,
                'id': entity.id,
                'post_id': post.id,
                'date': post.date.strftime('%Y-%m-%d %H:%M:%S') if post.date else 'N/A',
                'message': message_text,
                'link': f"https://t.me/{entity.username}/{post.id}" if entity.username else f"https://t.me/c/{entity.id}/{post.id}",
                'views': post.views if hasattr(post, 'views') else 'N/A',
                'reactions': sum(reaction.count for reaction in post.reactions.results) if hasattr(post, 'reactions') and post.reactions else 0,
                'forwards': post.forwards if hasattr(post, 'forwards') else 'N/A',
                'comments_count': comments_count,
                'category': category
            }

            data.append(combined_message)

        data_id = str(uuid.uuid4())
        os.makedirs('temp_data', exist_ok=True)
        with open(f'temp_data/{data_id}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f)

        logging.debug(f"Fetched data: {data}")
        logging.debug(f"Data ID: {data_id}")

        return data, data_id
    finally:
        if client.is_connected():
            await client.disconnect()

def index(request):
    return render(request, 'myapp/base.html')

async def telegram_view(request):
    cleanup_temp_data()

    filters = request.GET.getlist('filter')
    channel_url = request.GET.get('channel_url', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    data_id = request.GET.get('data_id', '')
    sort_by = request.GET.get('sort_by', 'date')
    sort_direction = request.GET.get('sort_direction', 'desc')

    if request.method == 'POST':
        form = TelegramForm(request.POST)
        if form.is_valid():
            channel_urls = form.cleaned_data['channel_url'].strip().split('\n')
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            all_data = []
            data_id_list = []

            for channel_url in channel_urls:
                channel_url = channel_url.strip()
                if channel_url:
                    data, data_id = await fetch_telegram_data(channel_url, start_date, end_date)
                    all_data.extend(data)
                    data_id_list.append(data_id)
            
            combined_data_id = str(uuid.uuid4())
            with open(f'temp_data/{combined_data_id}.json', 'w', encoding='utf-8') as f:
                json.dump(all_data, f)

            unique_titles = sorted(list(set(item['title'] for item in all_data)))
            logging.debug(f"Combined data passed to template: {all_data}")
            logging.debug(f"Combined Data ID passed to template: {combined_data_id}")
            
            filtered_data = [item for item in all_data if not filters or 'all' in filters or item['title'] in filters]
            
            # Сортировка данных
            reverse = sort_direction == 'desc'
            if sort_by == 'channel':
                filtered_data.sort(key=lambda x: x['title'], reverse=reverse)
            elif sort_by == 'postid':
                filtered_data.sort(key=lambda x: x['post_id'], reverse=reverse)
            elif sort_by == 'date':
                filtered_data.sort(key=lambda x: x['date'], reverse=reverse)
            elif sort_by == 'category':
                filtered_data.sort(key=lambda x: x['category'], reverse=reverse)

            paginator = Paginator(filtered_data, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, 'myapp/telegram_form.html', {
                'form': form,
                'parsed_data': page_obj,
                'data_id': combined_data_id,
                'filters': filters,
                'unique_titles': unique_titles,
                'channel_url': request.POST.get('channel_url'),
                'start_date': request.POST.get('start_date'),
                'end_date': request.POST.get('end_date'),
                'sort_by': sort_by,
                'sort_direction': sort_direction,
                'unique_categories': get_unique_categories(),
            })
    else:
        form = TelegramForm(initial={
            'channel_url': channel_url,
            'start_date': start_date,
            'end_date': end_date,
        })
    
    parsed_data = []
    if data_id:
        with open(f'temp_data/{data_id}.json', 'r', encoding='utf-8') as f:
            parsed_data = json.load(f)
    
    unique_titles = sorted(list(set(item['title'] for item in parsed_data)))
    
    filtered_data = [item for item in parsed_data if not filters or 'all' in filters or item['title'] in filters]
    
    # Сортировка данных
    reverse = sort_direction == 'desc'
    if sort_by == 'channel':
        filtered_data.sort(key=lambda x: x['title'], reverse=reverse)
    elif sort_by == 'postid':
        filtered_data.sort(key=lambda x: x['post_id'], reverse=reverse)
    elif sort_by == 'date':
        filtered_data.sort(key=lambda x: x['date'], reverse=reverse)
    elif sort_by == 'category':
        filtered_data.sort(key=lambda x: x['category'], reverse=reverse)

    paginator = Paginator(filtered_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'myapp/telegram_form.html', {
        'form': form,
        'parsed_data': page_obj,
        'data_id': data_id,
        'filters': filters,
        'unique_titles': unique_titles,
        'channel_url': channel_url,
        'start_date': start_date,
        'end_date': end_date,
        'sort_by': sort_by,
        'sort_direction': sort_direction,
        'unique_categories': get_unique_categories(),
    })

def export_to_excel(request):
    data_id = request.GET.get('data_id')
    if not data_id:
        return HttpResponse("No data ID provided.", status=400)

    file_path = f"temp_data/{data_id}.json"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            parsed_data = json.load(f)
    except FileNotFoundError:
        return HttpResponse("Data file not found.", status=404)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Telegram Data'
    
    headers = ['Канал', 'ID Канала', 'ID Поста', 'Дата', 'Сообщение', 'Категория', 'Ссылка', 'Просмотров', 'Реакции', 'Пересылки', 'Комментарии']
    sheet.append(headers)

    for item in parsed_data:
        row = [
            item['title'], 
            item['id'], 
            item['post_id'], 
            item['date'], 
            item['message'], 
            item['category'],
            item['link'], 
            item['views'], 
            item['reactions'], 
            item['forwards'],
            item['comments_count']
        ]
        sheet.append(row)

    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=telegram_data_{current_time}.xlsx'
    workbook.save(response)
    
    return response

async def get_post_details(request):
    if request.method == 'GET':
        post_id = request.GET.get('post_id')
        channel_id = request.GET.get('channel_id')
        page = int(request.GET.get('page', 1))
        limit = 10

        if not post_id or not channel_id:
            logging.error(f"Missing or empty post_id or channel_id: post_id={post_id}, channel_id={channel_id}")
            return JsonResponse({'error': 'Missing post_id or channel_id'}, status=400)

        client = TelegramClient('session_name', api_id, api_hash)
        try:
            if not client.is_connected():
                await client.connect()
            if not await client.is_user_authorized():
                print("Please enter your phone number (e.g., +79991234567): ")
                phone = input().strip()
                await client.start(phone=phone)

            entity = await client.get_entity(int(channel_id))
            post = await client.get_messages(entity, ids=int(post_id))

            if not post:
                logging.error(f"Post {post_id} not found for channel {channel_id}")
                return JsonResponse({'error': 'Post not found'}, status=404)

            if isinstance(post, types.Message):
                reactions = []
                if hasattr(post, 'reactions') and post.reactions:
                    for reaction in post.reactions.results:
                        reaction_type = reaction.reaction
                        logging.debug(f"Reaction type: {type(reaction_type).__name__}, Reaction: {reaction_type}")
                        if isinstance(reaction_type, types.ReactionEmoji):
                            reactions.append({
                                'emoticon': reaction_type.emoticon,
                                'count': reaction.count
                            })
                        elif isinstance(reaction_type, types.ReactionPaid):
                            reactions.append({
                                'emoticon': '💎',
                                'count': reaction.count
                            })
                        else:
                            logging.warning(f"Unknown reaction type: {type(reaction_type).__name__}")
                            reactions.append({
                                'emoticon': '[Неизвестная реакция]',
                                'count': reaction.count
                            })

                comments_data = []
                if hasattr(post, 'replies') and post.replies and post.replies.replies > 0:
                    async for comment in client.iter_messages(entity, reply_to=post.id, limit=50):
                        if isinstance(comment, types.Message):
                            author = await comment.get_sender()
                            author_name = author.username if author and hasattr(author, 'username') else 'Аноним'

                            comment_replies = comment.replies.replies if hasattr(comment, 'replies') and comment.replies and comment.replies.replies is not None else 0
                            comment_forwards = comment.forwards if hasattr(comment, 'forwards') and comment.forwards is not None else 0

                            comments_data.append({
                                'message': comment.message or '[Без текста]',
                                'date': comment.date.strftime('%Y-%m-%d %H:%M:%S') if comment.date else 'N/A',
                                'author': author_name,
                                'forwards': comment_forwards,
                                'replies': comment_replies
                            })
                    logging.debug(f"Fetched {len(comments_data)} comments for post {post_id}")
                else:
                    logging.debug(f"No replies found for post {post_id}")

                total_comments = len(comments_data)
                start = (page - 1) * limit
                end = min(start + limit, total_comments)
                paginated_comments = comments_data[start:end]

                response_data = {
                    'reactions': reactions,
                    'comments': paginated_comments,
                    'total_comments': total_comments
                }
                logging.debug(f"Returning response: {response_data}")
                return JsonResponse(response_data)
            else:
                logging.error(f"Invalid post data for post {post_id}")
                return JsonResponse({'error': 'Invalid post data'}, status=400)
        except Exception as e:
            logging.error(f"Error in get_post_details: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if client.is_connected():
                await client.disconnect()

def update_post_category(request):
    """
    Обновляет категорию поста и добавляет данные для переобучения модели.
    """
    global model, vectorizer
    if request.method == 'POST':
        data_id = request.POST.get('data_id')
        post_id = request.POST.get('post_id')
        new_category = request.POST.get('category')

        if not all([data_id, post_id, new_category]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Загружаем текущие данные
        file_path = f"temp_data/{data_id}.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                parsed_data = json.load(f)
        except FileNotFoundError:
            return JsonResponse({'error': 'Data file not found'}, status=404)

        # Находим и обновляем категорию поста
        updated = False
        for item in parsed_data:
            if str(item['post_id']) == post_id:
                item['category'] = new_category
                updated = True
                break

        if not updated:
            return JsonResponse({'error': 'Post not found'}, status=404)

        # Сохраняем обновленные данные
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f)

        # Формируем данные для обновления модели
        new_data = [{
            'Text': item['message'],
            'Category ': new_category
        } for item in parsed_data if str(item['post_id']) == post_id]

        # Обновляем модель с новыми данными, передаём путь к temp_data
        update_model(new_data, temp_data_path=file_path)
        model, vectorizer = load_model()  # Перезагружаем модель после обновления

        return JsonResponse({'success': True, 'message': 'Category updated and model retrained'})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def export_model_view(request):
    """
    Экспортирует модель и векторизатор в указанную директорию.
    """
    if request.method == 'GET':
        export_path = request.GET.get('path', 'exported_model')
        success = export_model(export_path)
        if success:
            return JsonResponse({'success': True, 'message': f'Model exported to {export_path}'})
        return JsonResponse({'success': False, 'error': 'Failed to export model'}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)