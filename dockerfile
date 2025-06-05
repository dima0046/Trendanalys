ROM python:3.11-slim

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

# Создаём debug.log как файл, если он отсутствует или является директорией
RUN rm -rf debug.log && touch debug.log && chmod 664 debug.log

# Собираем статические файлы
RUN python manage.py collectstatic --noinput --settings=myproject.settings

EXPOSE 8000

# Установка временной зоны
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Команда по умолчанию
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "myproject.wsgi:application"]