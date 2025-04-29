import asyncio
from datetime import datetime
from telethon import TelegramClient, utils, types

# Замените следующие строки своими данными
api_id = '21954039'
api_hash = '00d97492fc67b0c458e7e7722d61ec76'
client = TelegramClient('session_name', api_id, api_hash)

async def fetch_telegram_data(channels):
    await client.start()
    
    data = []

    for channel in channels:
        try:
            if "https://t.me/" in channel:
                channel = channel.split('/')[-1]  # Получаем последнюю часть URL
            elif "https://web.telegram.org/k/#" in channel:
                channel_id = int(channel.split('#')[-1])
                channel = utils.get_peer_id(types.PeerChannel(channel_id))

            entity = await client.get_entity(channel)
            posts = await client.get_messages(entity, limit=100)

            for post in posts:
                if post.date.timestamp() < datetime.now().timestamp() - 7 * 86400:
                    continue  # Пропускаем посты старше одной недели

                views = post.views if hasattr(post, 'views') else 'N/A'
                reactions_count = 0
                if hasattr(post, 'reactions') and post.reactions:
                    reactions_count = sum(reaction.count for reaction in post.reactions.results)

                reposts = post.forwards if hasattr(post, 'forwards') else 'N/A'
                comments = 'NONE'
                if hasattr(post, 'comments'):
                    if post.comments:
                        comments = 'ALLOWED'

                post_link = f"https://t.me/{entity.username}/{post.id}" if entity.username else f"https://t.me/c/{entity.id}/{post.id}"

                data.append([
                    entity.title,
                    entity.id,
                    post.id,
                    post.date.strftime('%Y-%m-%d %H:%M:%S'),
                    post.message,
                    post_link,
                    views,
                    reactions_count,
                    reposts,
                    comments
                ])
        except Exception as e:
            print(f"Error for channel {channel}: {e}")

    return data

# Пример использования
channels = ["https://t.me/some_channel", "https://web.telegram.org/k/#123456789"]
data = asyncio.run(fetch_telegram_data(channels))
print(data)
