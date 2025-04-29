import json
from datetime import datetime
from telethon import TelegramClient, utils, types
import asyncio
#from telethon.tl.functions.messages import get_discussion_replies_count
from telethon.tl.types import InputPeerChannel, InputMessageID

api_id = '21954039'
api_hash = '00d97492fc67b0c458e7e7722d61ec76'
client = TelegramClient('session_name', api_id, api_hash)


def datetime_converter(o):
    if isinstance(o, datetime):
        return o.__str__()

async def fetch_single_post():
    await client.start()

    # URL канала
    channel_url = 'https://t.me/ru2ch'
    username = channel_url.split('/')[-1]  # Получаем последнюю часть URL

    entity = await client.get_entity(username)
    print(entity.stringify())

    async for message in client.get_discussion_replies_count('https://t.me/ru2ch', 112530):
        print(message)

    """
    async for post in client.iter_messages(entity, limit=1, reverse=True):
        # Преобразуем объект post в словарь
        post_dict = post.to_dict()

        # Получаем комментарии к посту
        if post.replies and post.replies.replies > 0:
            discussion_request = GetDiscussionMessageRequest(
                peer=entity,
                msg_id=post.id
            )
            discussion = await client(discussion_request)
            post_dict['comments_count'] = len(discussion.messages)
        else:
            post_dict['comments_count'] = 0

        # Сохраняем словарь в JSON файл
        with open('single_post.json', 'w', encoding='utf-8') as json_file:
            json.dump(post_dict, json_file, ensure_ascii=False, indent=4, default=datetime_converter)

        break  # Останавливаемся после первого поста

    await client.disconnect()

    """
    
# Пример использования:
asyncio.run(fetch_single_post())
