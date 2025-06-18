#!/bin/bash

# === Настройки ===
CONTAINER_NAME="trendanalys-db-1"  # или используй: $(docker-compose ps -q db)
DB_NAME="trendanalys"
DB_USER="trendanalys_user"
BACKUP_DIR="./db_backups"
DATE_SUFFIX=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/backup_$DATE_SUFFIX.sql"

# === Создание директории для бэкапов ===
mkdir -p "$BACKUP_DIR"

# === Создание дампа базы данных ===
echo "Создание бэкапа базы данных $DB_NAME..."
docker exec -t "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"

# === Проверка результата ===
if [[ $? -eq 0 ]]; then
    echo "✅ Бэкап успешно создан: $BACKUP_FILE"
else
    echo "❌ Ошибка при создании бэкапа"
fi
