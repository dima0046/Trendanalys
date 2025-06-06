```markdown
# Шпаргалка по PostgreSQL для базы данных Trendanalys

Эта шпаргалка содержит примеры SQL-запросов для работы с таблицей `myapp_telegrampost` в базе `trendanalys`, а также основные команды `psql` для управления базой данных. Таблица `myapp_telegrampost` предполагает наличие полей: `id` (integer), `channel_id` (integer), `date` (date), `created_at` (timestamp with time zone), `message` (text), `link` (text).

## Подключение к базе данных

### Через `psql` в Docker
```bash
docker-compose exec db psql -U trendanalys_user -d trendanalys
```

- Пользователь: `trendanalys_user`
- Пароль: `trendanalys_pass` (если запрашивается)
- База: `trendanalys`

### Через pgAdmin (на Windows)

- **Host**: `<server-ip>` (публичный или локальный IP сервера)
- **Port**: `5432`
- **Database**: `trendanalys`
- **Username**: `trendanalys_user`
- **Password**: `****`

## Основные команды `psql`

| Команда                     | Описание                                                            |
| ---------------------------------- | --------------------------------------------------------------------------- |
| `\l`                             | Список всех баз данных                                   |
| `\c trendanalys`                 | Подключиться к базе `trendanalys`                        |
| `\dt`                            | Список таблиц в текущей базе                        |
| `\d myapp_telegrampost`          | Описание структуры таблицы `myapp_telegrampost`   |
| `\du`                            | Список пользователей и их ролей                  |
| `\q`                             | Выход из `psql`                                                    |
| `\i file.sql`                    | Выполнить SQL-скрипт из файла                         |
| `SET timezone = 'Europe/Paris';` | Установить часовой пояс (замените на ваш) |

### Выполнение запроса через терминал

```bash
docker-compose exec db psql -U trendanalys_user -d trendanalys -c "SELECT COUNT(*) FROM myapp_telegrampost;"
```

## Структура таблицы `myapp_telegrampost`

Предполагаемая структура (на основе ваших данных):

```sql
CREATE TABLE public.myapp_telegrampost (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER,
    date DATE,
    created_at TIMESTAMP WITH TIME ZONE,
    message TEXT,
    link TEXT
);
```

Проверить структуру:

```sql
\d public.myapp_telegrampost
```

## Примеры SQL-запросов

### 1. Выборка всех записей

Получить последние 10 сообщений:

```sql
SELECT 
    id,
    channel_id,
    date,
    created_at,
    message,
    link
FROM public.myapp_telegrampost
ORDER BY id DESC
LIMIT 10;
```

### 2. Фильтрация по дате

Записи за 03.06.2025 (по `created_at`):

```sql
SELECT 
    id,
    channel_id,
    created_at,
    message,
    link
FROM public.myapp_telegrampost
WHERE DATE(created_at) = '2025-06-03'
ORDER BY id DESC;
```

С учётом часового пояса (например, CEST):

```sql
SELECT 
    id,
    channel_id,
    created_at,
    message,
    link
FROM public.myapp_telegrampost
WHERE DATE(created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Paris') = '2025-06-03'
ORDER BY id DESC;
```

### 3. Проверка дублирования сообщений

Найти дубликаты по `link`:

```sql
SELECT 
    link,
    COUNT(*) AS count,
    ARRAY_AGG(id) AS post_ids,
    ARRAY_AGG(channel_id) AS channel_ids,
    ARRAY_AGG(created_at) AS created_ats,
    ARRAY_AGG(message) AS messages
FROM public.myapp_telegrampost
WHERE link IS NOT NULL
GROUP BY link
HAVING COUNT(*) > 1
ORDER BY count DESC;
```

Подробный список дубликатов:

```sql
SELECT 
    id,
    link,
    channel_id,
    created_at,
    message
FROM public.myapp_telegrampost
WHERE link IN (
    SELECT link
    FROM public.myapp_telegrampost
    WHERE link IS NOT NULL
    GROUP BY link
    HAVING COUNT(*) > 1
)
ORDER BY link, id DESC;
```

Дубликаты по `channel_id` и `message`:

```sql
SELECT 
    channel_id,
    message,
    COUNT(*) AS count,
    ARRAY_AGG(id) AS post_ids,
    ARRAY_AGG(created_at) AS created_ats
FROM public.myapp_telegrampost
WHERE message IS NOT NULL
GROUP BY channel_id, message
HAVING COUNT(*) > 1
ORDER BY count DESC;
```

### 4. Агрегация данных

Количество сообщений по каналам:

```sql
SELECT 
    channel_id,
    COUNT(*) AS post_count,
    MIN(created_at) AS first_post,
    MAX(created_at) AS last_post
FROM public.myapp_telegrampost
GROUP BY channel_id
ORDER BY post_count DESC;
```

Сообщения за последние 7 дней:

```sql
SELECT 
    DATE(created_at) AS post_date,
    COUNT(*) AS post_count
FROM public.myapp_telegrampost
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY post_date DESC;
```

### 5. Поиск по тексту

Найти сообщения, содержащие слово "test":

```sql
SELECT 
    id,
    channel_id,
    created_at,
    message
FROM public.myapp_telegrampost
WHERE message ILIKE '%test%'
ORDER BY created_at DESC;
```

- `ILIKE`: Регистронезависимый поиск.
- `%test%`: Любая подстрока с "test".

### 6. Обновление данных

Пометить дубликаты как удалённые (добавить поле `is_duplicate`):

```sql
ALTER TABLE myapp_telegrampost ADD COLUMN is_duplicate BOOLEAN DEFAULT FALSE;
UPDATE myapp_telegrampost
SET is_duplicate = TRUE
WHERE link IN (
    SELECT link
    FROM myapp_telegrampost
    WHERE link IS NOT NULL
    GROUP BY link
    HAVING COUNT(*) > 1
);
```

### 7. Удаление данных

Удалить дубликаты, оставив самую запись:

```sql
DELETE FROM myapp_telegrampost
WHERE id IN (
    SELECT id
    FROM (
        SELECT 
            id,
            ROW_NUMBER() OVER (PARTITION BY link ORDER BY created_at DESC) AS rn
        FROM public.myapp_telegrampost
        WHERE link IS NOT NULL
    ) t
    WHERE rn > 1
);
```

Удалить записи старше 30 дней:

```sql
DELETE FROM myapp_telegrampost
WHERE created_at < CURRENT_DATE - INTERVAL '30 days';
```

### 8. Проверка статистики

Диапазон дат в таблице:

```sql
SELECT 
    MIN(created_at) AS first_post,
    MAX(created_at) AS last_post,
    COUNT(*) AS total_posts
FROM myapp_telegrampost;
```

Размер таблицы:

```sql
SELECT pg_size_pretty(pg_total_relation_size('myapp_telegrampost')) AS table_size;
```

## Управление базой данных

### Создание резервной копии

Создать дамп базы:

```bash
docker-compose exec db pg_dump -U trendanalys_user trendanalys > backup.sql
```

### Восстановление из резервной копии

Очистить базу и восстановить:

```bash
docker-compose exec db psql -U trendanalys_user -d trendanalys -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker-compose exec db psql -U trendanalys_user -d trendanalys < backup.sql
```

### Изменение пароля пользователя

```sql
ALTER USER trendanalys_user WITH PASSWORD 'new_password';
```

### Проверка часового пояса

Текущий часовой пояс:

```sql
SHOW timezone;
```

Установить часовой пояс:

```sql
SET timezone = 'Europe/Paris';
```

## Полезные советы

- **Индексы для оптимизации**:
  Создать индекс для `link` (для проверки дубликатов):

  ```sql
  CREATE INDEX idx_myapp_telegrampost_link ON myapp_telegrampost(link);
  ```

  Для `created_at` (для фильтрации по дате):

  ```sql
  CREATE INDEX idx_myapp_telegrampost_created_at ON myapp_telegrampost(created_at);
  ```
- **Проверка производительности**:
  Анализировать запрос:

  ```sql
  EXPLAIN ANALYZE SELECT * FROM myapp_telegrampost WHERE DATE(created_at) = '2025-06-03';
  ```
- **Логи PostgreSQL**:
  Просмотреть логи:

  ```bash
  docker-compose logs db
  ```

## Устранение неполадок

- **Нет данных за дату**:

  ```sql
  SELECT COUNT(*) FROM myapp_telegrampost WHERE DATE(created_at) = '2025-06-03';
  ```

  Если `0`, запустите парсер:

  ```bash
  docker-compose exec web python manage.py shell
  ```

  ```python
  from myapp.telegram.tasks import run_daily_parser
  run_daily_parser.delay()
  ```
- **Ошибка подключения**:
  Проверьте `.env`:

  ```bash
  cat ~/Trendanalys/.env
  ```

  Убедитесь, что `DB_HOST=db`, `DB_USER=trendanalys_user`, `DB_PASSWORD=trendanalys_pass`.
- **Ошибка `avatar_path`**:
  Проверьте:

  ```bash
  grep avatar_path ~/Trendanalys/myapp/telegram/tasks.py
  ```

  Замените на `channel.avatar.url if channel.avatar else None`, перестройте:

  ```bash
  docker-compose build --no-cache
  docker-compose up -d
  ```

## Дополнительные ресурсы

- [Документация PostgreSQL](https://www.postgresql.org/docs/16/index.html)
- [pgAdmin Документация](https://www.pgadmin.org/docs/pgadmin4/latest/)
- [Docker Postgres](https://hub.docker.com/_/postgres)

```

```
