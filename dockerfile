FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=myproject.settings

WORKDIR /app

COPY requirements.txt .
RUN apt-get update \
    && apt-get install -y net-tools \
    && pip install --upgrade pip \
    && pip install --user -r requirements.txt

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=myproject.settings

WORKDIR /app

RUN apt-get update \
    && apt-get install -y net-tools

# Копируем зависимости из builder
COPY --from=builder /root/.local /root/.local

# Добавляем /root/.local/bin в PATH, чтобы gunicorn был доступен
ENV PATH="/root/.local/bin:$PATH"

COPY . .

RUN python manage.py collectstatic --noinput --settings=myproject.settings

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "myproject.wsgi:application"]