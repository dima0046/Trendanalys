from django.core.management.base import BaseCommand
from telethon import TelegramClient
from myapp.telegram.models import TelegramChannel
from dotenv import load_dotenv
from PIL import Image
import os
from asgiref.sync import sync_to_async
import asyncio

load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

class Command(BaseCommand):
    help = 'Обновляет аватары каналов и сохраняет их в модель TelegramChannel'

    def handle(self, *args, **options):
        print("👋 Команда запущена")
        asyncio.run(self.run())

    async def run(self):
        print("🚀 Запуск клиента Telegram...")
        client = TelegramClient('session_name', api_id, api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            print("❗ Telegram клиент не авторизован.")
            print("🔐 Пожалуйста, пройди ручную авторизацию (например, через Telethon CLI).")
            await client.disconnect()
            return

        channels = await sync_to_async(list)(TelegramChannel.objects.all())
        for channel in channels:
            print(f'🔄 Обработка канала: {channel.title} ({channel.url})')
            try:
                entity = await client.get_entity(channel.url)
                photo_path = await client.download_profile_photo(entity)

                if photo_path:
                    print(f'📷 Фото скачано: {photo_path}')
                    filename = f"channel_{entity.id}.jpg"
                    save_path = os.path.join('myapp', 'static', 'media', 'avatars', filename)
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)

                    img = Image.open(photo_path)
                    img = img.resize((50, 50), Image.LANCZOS)
                    img.save(save_path, 'JPEG', quality=85)

                    channel.avatar = f"media/avatars/{filename}"  # путь от STATIC_URL
                    await sync_to_async(channel.save)()

                    print(f'✅ Аватар сохранён: {filename}')
                else:
                    print(f'⚠ Нет фото у: {channel.title}')

            except Exception as e:
                print(f'❌ Ошибка при обработке {channel.url}: {e}')

        await client.disconnect()
        print("✅ Готово.")
