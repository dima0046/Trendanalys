# Шпаргалка по работе с Git на сервере при обновлениях (git pull)

Эта шпаргалка поможет разобраться, когда достаточно выполнить `git pull` для обновления кода на сервере, а когда требуется пересобрать проект (например, перезапустить контейнеры, выполнить миграции или установить зависимости).

## Основные команды для обновления
1. **Перейти в директорию проекта**:
   ```bash
   cd /path/to/your/project
   ```

2. **Обновить код**:
   ```bash
   git pull origin main
   ```
   Замените `main` на вашу ветку, если она отличается (например, `develop`).

3. **Проверить статус**:
   ```bash
   git status
   ```
   Убедитесь, что нет конфликтов или незакоммиченных изменений.

## Когда достаточно просто `git pull`
`git pull` достаточно, если обновления **не затрагивают**:
- Зависимости (например, `requirements.txt`, `package.json`).
- Миграции базы данных.
- Конфигурацию сервера или Docker-файлы (`Dockerfile`, `docker-compose.yml`).
- Статические файлы, требующие сборки (`collectstatic`).

**Примеры ситуаций**:
- Изменены HTML-шаблоны, CSS, JavaScript (без новых npm-зависимостей).
- Обновлён код Python/Django, не требующий новых библиотек или миграций.
- Исправлены баги в логике без изменения структуры проекта.

**Действия**:
```bash
git pull origin main
sudo systemctl restart gunicorn  # Или ваш сервис (например, uwsgi, nginx)
```
Если используется Docker:
```bash
docker-compose restart web  # Перезапустить только сервис
```

## Когда нужно пересобирать проект
Пересборка нужна, если обновления затрагивают:
- **Зависимости**:
  - Обновлён `requirements.txt` (Python).
  - Изменён `package.json` или `package-lock.json` (Node.js).
- **Миграции базы данных**:
  - Новые или изменённые файлы в `migrations/`.
- **Конфигурация**:
  - Изменения в `Dockerfile`, `docker-compose.yml`, `.env`.
- **Статические файлы**:
  - Новые или изменённые файлы, требующие `python manage.py collectstatic`.
- **Системные изменения**:
  - Обновлены системные пакеты или конфигурации сервера.

**Примеры ситуаций**:
- Добавлена новая библиотека в `requirements.txt`.
- Создана новая миграция (`0002_some_migration.py`).
- Изменён порт или сервисы в `docker-compose.yml`.
- Обновлён фронтенд с новыми npm-пакетами.

**Действия для Django-проекта без Docker**:
```bash
git pull origin main
pip install -r requirements.txt  # Обновить зависимости
python manage.py migrate  # Применить миграции
python manage.py collectstatic --noinput  # Собрать статические файлы
sudo systemctl restart gunicorn  # Перезапустить Gunicorn
sudo systemctl restart nginx  # Перезапустить Nginx, если нужно
```

**Действия для Docker-проекта**:
```bash
git pull origin main
docker-compose down  # Остановить контейнеры
docker-compose build  # Пересобрать образы
docker-compose up -d  # Запустить контейнеры
docker-compose exec web python manage.py migrate  # Применить миграции
docker-compose exec web python manage.py collectstatic --noinput  # Собрать статические файлы
```

## Как определить, что нужно пересобирать
1. **