FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=myproject.settings \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Устанавливаем зависимости системы для PostgreSQL
RUN apt-get update && apt-get install -y \
    net-tools \
    gcc \
    libc-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --user -r requirements.txt \
    && pip show psycopg2-binary  # Проверяем установку psycopg2-binary

# Копируем проект
COPY . .

# Собираем статические файлы
RUN python manage.py collectstatic --noinput --settings=myproject.settings

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "myproject.wsgi:application"]