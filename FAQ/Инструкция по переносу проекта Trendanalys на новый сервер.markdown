# Инструкция по переносу проекта Trendanalys на новый сервер

## 1. Подготовка нового сервера

1. **Убедитесь, что сервер соответствует требованиям**:
   - Минимальные ресурсы: 4 vCPU, 8 ГБ RAM.
   - Рекомендуемые ресурсы: 8–12 vCPU, 32 ГБ RAM.
   - Свободное место на диске: минимум 20 ГБ.
   - ОС: Linux (например, Ubuntu 22.04 LTS).
   - Установите Docker и Docker Compose:
     ```bash
     sudo apt update
     sudo apt install -y docker.io docker-compose
     sudo systemctl start docker
     sudo systemctl enable docker
     sudo usermod -aG docker $USER
     ```
     Перезайдите в сессию, чтобы применить изменения.

2. **Скопируйте проект на новый сервер**:
   - Скопируйте папку `Trendanalys` с текущего сервера на новый:
     ```bash
     scp -r root@dima0046:~/Trendanalys ~/Trendanalys
     ```
   - Убедитесь, что файл `session_name.session` (для Telegram авторизации) скопирован:
     ```bash
     ls -l ~/Trendanalys/session_name.session
     ```
     Если файла нет, скопируйте его отдельно:
     ```bash
     scp root@dima0046:~/Trendanalys/session_name.session ~/Trendanalys/
     ```

3. **Проверьте зависимости**:
   - Убедитесь, что в папке `Trendanalys` есть файлы `docker-compose.yml`, `Dockerfile` (если есть), `.env`, и код проекта (`myproject`, `myapp`).

## 2. Настройка файла `.env`

1. Откройте или создайте файл `.env` в корне проекта (`~/Trendanalys/.env`):
   ```bash
   nano ~/Trendanalys/.env
   ```
2. Убедитесь, что в нём указаны следующие переменные (замените значения на свои, если нужно):
   ```
   # Настройки базы данных
   DB_NAME=trendanalys
   DB_USER=trendanalys_user
   DB_PASSWORD=your_password
   DB_HOST=db
   DB_PORT=5432

   # Настройки Celery и Redis
   CELERY_BROKER_URL=redis://redis:6379/0
   CELERY_RESULT_BACKEND=redis://redis:6379/0

   # Настройки Django
   SECRET_KEY=your_secret_key
   DEBUG=False
   ALLOWED_HOSTS=localhost,127.0.0.1,your_server_ip

   # Настройки Telegram (замените на свои значения)
   API_ID=your_api_id
   API_HASH=your_api_hash
   ```
   - Убедитесь, что `CELERY_BROKER_URL` и `CELERY_RESULT_BACKEND` указывают на `redis`, а не `localhost`.

## 3. Проверка `docker-compose.yml`

1. Откройте файл `docker-compose.yml`:
   ```bash
   nano ~/Trendanalys/docker-compose.yml
   ```
2. Убедитесь, что он содержит сервисы `web`, `db`, `redis`, `celery_worker`, `celery_beat`, и что `.env` монтируется:
   ```yaml
   version: '3.8'

   services:
     web:
       build: .
       command: gunicorn --bind 0.0.0.0:8000 myproject.wsgi:application
       volumes:
         - .:/app
         - ./.env:/app/.env
       ports:
         - "8000:8000"
       depends_on:
         - db
         - redis
       env_file:
         - .env

     db:
       image: postgres:16-alpine
       volumes:
         - postgres_data:/var/lib/postgresql/data
       environment:
         - POSTGRES_DB=${DB_NAME}
         - POSTGRES_USER=${DB_USER}
         - POSTGRES_PASSWORD=${DB_PASSWORD}
       ports:
         - "5432:5432"

     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"

     celery_worker:
       build: .
       command: celery -A myproject worker --loglevel=info
       volumes:
         - .:/app
         - ./.env:/app/.env
       depends_on:
         - db
         - redis
       env_file:
         - .env

     celery_beat:
       build: .
       command: celery -A myproject beat --loglevel=info
       volumes:
         - .:/app
         - ./.env:/app/.env
       depends_on:
         - db
         - redis
       env_file:
         - .env

   volumes:
     postgres_data:
   ```
   - Убедитесь, что `env_file: - .env` указано для всех сервисов.

## 4. Настройка `settings.py`

1. Откройте файл `~/Trendanalys/myproject/settings.py`:
   ```bash
   nano ~/Trendanalys/myproject/settings.py
   ```
2. Убедитесь, что настройки Celery и часового пояса корректны:
   ```python
   # Часовой пояс
   TIME_ZONE = 'Europe/Moscow'
   USE_TZ = True

   # Настройки Celery
   CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
   CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
   CELERY_ACCEPT_CONTENT = ['json']
   CELERY_TASK_SERIALIZER = 'json'
   CELERY_RESULT_SERIALIZER = 'json'
   CELERY_TIMEZONE = 'Europe/Moscow'

   # Расписание задач
   CELERY_BEAT_SCHEDULE = {
       'run-daily-telegram-parser': {
           'task': 'myapp.telegram.tasks.run_daily_parser',
           'schedule': crontab(hour=0, minute=0),  # Каждый день в 00:00
       },
   }
   ```
   - Убедитесь, что `CELERY_BROKER_URL` и `CELERY_RESULT_BACKEND` используют `redis`, а не `localhost`.

## 5. Настройка часового пояса в контейнерах

1. Часовой пояс в контейнерах должен быть `Europe/Moscow`. Добавьте настройку в `Dockerfile` (если его нет, создайте в корне проекта):
   ```dockerfile
   FROM python:3.11

   RUN apt update && apt install -y tzdata && \
       ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime && \
       dpkg-reconfigure -f noninteractive tzdata

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   ```
2. Пересоберите образы:
   ```bash
   docker-compose build
   ```
3. Если не хотите изменять `Dockerfile`, настройте часовой пояс вручную после запуска контейнеров:
   ```bash
   docker-compose exec web bash -c "apt update && apt install -y tzdata && ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime && dpkg-reconfigure -f noninteractive tzdata"
   docker-compose exec celery_beat bash -c "apt update && apt install -y tzdata && ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime && dpkg-reconfigure -f noninteractive tzdata"
   docker-compose exec celery_worker bash -c "apt update && apt install -y tzdata && ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime && dpkg-reconfigure -f noninteractive tzdata"
   ```
4. Проверьте время:
   ```bash
   docker-compose exec web date
   docker-compose exec celery_beat date
   docker-compose exec celery_worker date
   ```
   Ожидаемый вывод: `Sat May 31 16:57:00 MSK 2025` (с учётом текущего времени).

## 6. Запуск проекта

1. Запустите все сервисы:
   ```bash
   docker-compose up -d
   ```
2. Проверьте статус контейнеров:
   ```bash
   docker-compose ps
   ```
   Все сервисы (`web`, `db`, `redis`, `celery_worker`, `celery_beat`) должны быть в статусе `Up`.

## 7. Проверка подключения к Redis

1. Убедитесь, что Redis работает:
   ```bash
   docker-compose exec redis redis-cli ping
   ```
   Ожидаемый ответ: `PONG`.
2. Проверьте, что Celery использует правильный брокер:
   ```bash
   docker-compose exec web env | grep CELERY
   ```
   Ожидаемый вывод:
   ```
   CELERY_BROKER_URL=redis://redis:6379/0
   CELERY_RESULT_BACKEND=redis://redis:6379/0
   ```
3. Проверьте статус Celery:
   ```bash
   docker-compose exec web celery -A myproject status
   ```
   Ожидаемый вывод должен включать:
   ```
   - ** ---------- .> transport:   redis://redis:6379/0
   - ** ---------- .> results:     redis://redis:6379/0
   ```

## 8. Проверка Telegram авторизации

1. Убедитесь, что файл `session_name.session` присутствует:
   ```bash
   ls -l ~/Trendanalys/session_name.session
   ```
2. Проверьте авторизацию:
   ```bash
   docker-compose exec web python manage.py shell
   ```
   ```python
   from telethon import TelegramClient
   client = TelegramClient('session_name', api_id='your_api_id', api_hash='your_api_hash')
   client.start()
   print(client.is_user_authorized())
   ```
   - Замените `your_api_id` и `your_api_hash` на значения из `.env`.
   - Если вывод `False`, авторизуйтесь вручную (введите код при запросе).

## 9. Проверка выполнения задачи

1. Проверьте, что задача `run-daily-telegram-parser` запланирована:
   ```bash
   docker-compose exec web python manage.py shell
   ```
   ```python
   from django_celery_beat.models import PeriodicTask
   print(PeriodicTask.objects.all())
   ```
   Ожидаемый вывод:
   ```
   <PeriodicTaskQuerySet [<PeriodicTask: run-daily-telegram-parser: 0 0 * * * (m/h/dM/MY/d) Europe/Moscow>]>
   ```
2. Для теста измените расписание на каждые 5 минут:
   ```python
   from django_celery_beat.models import PeriodicTask, CrontabSchedule
   schedule, _ = CrontabSchedule.objects.get_or_create(minute='*/5')
   task = PeriodicTask.objects.get(name='run-daily-telegram-parser')
   task.crontab = schedule
   task.save()
   ```
3. Проверьте логи Celery Beat через 5 минут:
   ```bash
   docker-compose logs celery_beat
   ```
   Ищите:
   ```
   [INFO] Scheduler: Sending due task run-daily-telegram-parser
   ```
4. Проверьте логи Celery Worker:
   ```bash
   docker-compose logs celery_worker
   ```
   Ищите:
   ```
   [INFO] Task myapp.telegram.tasks.run_daily_parser succeeded
   ```
5. Проверьте базу данных:
   ```bash
   docker-compose exec db psql -U trendanalys_user -d trendanalys -c "SELECT * FROM myapp_telegrampost LIMIT 5;"
   docker-compose exec db psql -U trendanalys_user -d trendanalys -c "SELECT * FROM myapp_parserlog;"
   ```
   Должны появиться записи.
6. Проверьте логи:
   ```bash
   docker cp trendanalys-web-1:/app/debug.log debug.log
   cat debug.log
   ```
   Ищите:
   ```
   INFO 2025-05-31 myapp.telegram.tasks Запуск задачи run_daily_parser
   ```
7. Верните расписание на 00:00 MSK:
   ```python
   schedule, _ = CrontabSchedule.objects.get_or_create(hour=0, minute=0)
   task = PeriodicTask.objects.get(name='run-daily-telegram-parser')
   task.crontab = schedule
   task.save()
   ```

## 10. Проверка логов

1. Убедитесь, что логи пишутся корректно:
   ```bash
   docker-compose exec web ls -l /app/debug.log
   ```
   Права должны быть `664`. Если нет:
   ```bash
   docker-compose exec web chmod 664 /app/debug.log
   ```

## 11. Мониторинг ресурсов

1. Проверьте использование ресурсов:
   ```bash
   docker stats
   df -h
   ```
   - Убедитесь, что RAM и диск не исчерпаны.

## 12. Устранение неполадок

1. **Если Celery не подключается к Redis**:
   - Проверьте `CELERY_BROKER_URL`:
     ```bash
     docker-compose exec web env | grep CELERY
     ```
   - Убедитесь, что Redis работает:
     ```bash
     docker-compose exec redis redis-cli ping
     ```
2. **Если задача не выполняется**:
   - Проверьте логи Celery Beat и Worker:
     ```bash
     docker-compose logs celery_beat
     docker-compose logs celery_worker
     ```
   - Проверьте время:
     ```bash
     docker-compose exec web date
     ```
3. **Если база данных пуста**:
   - Убедитесь, что Telegram авторизация работает (см. шаг 8).
   - Запустите задачу вручную:
     ```bash
     docker-compose exec web celery -A myproject call myapp.telegram.tasks.run_daily_parser
     ```

---

## Итог

Эта инструкция охватывает все шаги, необходимые для переноса проекта `Trendanalys`:
- Перенос проекта на новый сервер.
- Настройка `.env` и `settings.py`.
- Исправление подключения к Redis.
- Настройка часового пояса.
- Проверка выполнения задач.

Если возникнут проблемы при переносе, сохраните логи (`docker-compose logs`) и проверьте шаги ещё раз. Удачи с переносом проекта!