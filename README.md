# Trendanalys

Trendanalys — это Django-проект для парсинга и анализа данных из Telegram-каналов. Проект позволяет собирать посты, реакции, комментарии, а также категоризировать сообщения с помощью OpenAI API. Вы можете фильтровать данные, экспортировать их в Excel и сохранять в базу данных SQLite.

## Особенности

- Парсинг постов из Telegram-каналов с помощью `Telethon`.
- Автоматическая категоризация сообщений через OpenAI API.
- Экспорт данных в Excel.
- Фильтрация данных по каналам.
- Интерактивный интерфейс с использованием Bootstrap 5.
- Сохранение данных в базу данных SQLite.

## Требования

- Python 3.8 или выше
- Виртуальное окружение
- Установленные зависимости из `requirements.txt`

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/dima0046/Trendanalys.git
   cd Trendanalys
   ```

2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Для Windows
   # или
   source .venv/bin/activate  # Для Linux/Mac
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Скопируйте `.env.example` в `.env` и заполните переменные:
   ```bash
   copy .env.example .env  # Для Windows
   # или
   cp .env.example .env  # Для Linux/Mac
   ```
   Укажите ваши `API_ID`, `API_HASH` (для Telegram) и `OPENAI_API_KEY`. Пример `.env`:
   ```
   API_ID=your_api_id
   API_HASH=your_api_hash
   OPENAI_API_KEY=your_openai_api_key
   ```

5. Примените миграции для создания базы данных:
   ```bash
   python manage.py migrate
   ```

6. Запустите сервер:
   ```bash
   runserver.bat  # Для Windows
   # или
   uvicorn Trendanalys.asgi:application --host 127.0.0.1 --port 8000  # Для Linux/Mac
   ```

7. Откройте браузер и перейдите по адресу `http://127.0.0.1:8000/telegram/`.

## Использование

1. На странице `http://127.0.0.1:8000/telegram/` введите URL Telegram-канала (например, `https://t.me/channel_name`).
2. Укажите даты начала и окончания для парсинга (опционально).
3. Нажмите "Загрузить", чтобы получить данные.
4. Используйте фильтры для выбора каналов.
5. Нажмите "Excel" для экспорта данных или "Сохранить модель" для сохранения в базу данных.
6. Кликните на пост, чтобы увидеть детали (реакции, комментарии).

## Зависимости

Список зависимостей указан в `requirements.txt`:

- `django==5.1.1`
- `django-bootstrap5==24.3`
- `django-filter==24.3`
- `telethon==1.36.0`
- `pandas==2.2.3`
- `openpyxl==3.1.5`
- `scikit-learn==1.5.2`
- `nltk==3.9.1`
- `openai==1.52.0`
- `requests==2.32.3`
- `python-dateutil==2.9.0.post0`
- `pytz==2024.2`
- `python-dotenv==1.0.1`
- `uvicorn==0.32.0`

## Примечания

- Убедитесь, что у вас есть файлы `pedro-raccoon-raccoon.gif` и `pedro-raccoon-raccoon.mp3` в директориях `myapp/static/myapp/gif/` и `myapp/static/myapp/audio/`. Если их нет, удалите ссылки на них в `telegram_form.html`.
- Проект использует асинхронные функции, поэтому для запуска сервера требуется `uvicorn`.
- Файлы `db.sqlite3` и `session_name.session` создаются автоматически при первом запуске и не должны быть добавлены в репозиторий Git.

## Лицензия

MIT License

Copyright (c) 2025 @dima0046

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.