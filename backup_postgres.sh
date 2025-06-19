#!/bin/bash

# === Настройки ===
CONTAINER_NAME="trendanalys-db-1"  # Имя контейнера PostgreSQL
DB_NAME="trendanalys"
DB_USER="trendanalys_user"
BACKUP_DIR="./db_backups"
DATE_SUFFIX=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/backup_$DATE_SUFFIX.sql"
DAYS_TO_KEEP=7

# === Создание директории для бэкапов ===
mkdir -p "$BACKUP_DIR"

# === Создание дампа базы данных ===
echo "📦 Создание бэкапа базы данных $DB_NAME..."
docker exec -t "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"

# === Проверка результата ===
if [[ $? -eq 0 ]]; then
    echo "✅ Бэкап успешно создан: $BACKUP_FILE"
else
    echo "❌ Ошибка при создании бэкапа"
    exit 1
fi

# === Удаление старых бэкапов ===
echo "🧹 Удаление бэкапов старше $DAYS_TO_KEEP дней..."
find "$BACKUP_DIR" -type f -name "backup_*.sql" -mtime +$DAYS_TO_KEEP -exec rm {} \;

echo "🟢 Готово."
