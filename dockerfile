FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=myproject.settings \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Устанавливаем зависимости системы для PostgreSQL и net-tools
RUN apt-get update && apt-get install -y \
    net-tools \
    gcc \
    libc-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip и устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --user -r requirements.txt

# Копируем проект
COPY . .

# Собираем статические файлы
RUN python manage.py collectstatic --noinput --settings=myproject.settings

EXPOSE 8000

# Команда по умолчанию (переопределяется в docker-compose)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "myproject.wsgi:application"]