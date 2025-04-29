# singleton.py
from pyrogram import Client as PyroClient

class TelegramClient:
    instance = None
    is_started = False

    @classmethod
    def get_client(cls):
        if cls.instance is None:
            api_id = '21954039'  # Replace with your actual api_id
            api_hash = '00d97492fc67b0c458e7e7722d61ec76'  # Replace with your actual api_hash
            cls.instance = PyroClient("pyrogram_session_name", api_id=api_id, api_hash=api_hash)
        return cls.instance

    @classmethod
    async def fetch_data(cls, channel_url, start_date, end_date):
        client = cls.get_client()
        if not cls.is_started:
            await client.start()
            cls.is_started = True

        try:
            chat = await client.get_chat(channel_url)
            messages = []
            async for message in client.get_chat_history(chat.id):
                if start_date <= message.date.date() <= end_date:
                    messages.append({
                        "text": message.text,
                        "date": message.date,
                        "views": message.views,
                        "reactions": len(message.reactions.reactions) if message.reactions else 0
                    })
            return messages
        finally:
            await client.stop()
            cls.is_started = False