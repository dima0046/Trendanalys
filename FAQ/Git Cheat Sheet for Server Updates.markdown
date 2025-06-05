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
1. **Проверить изменения**:
   ```bash
   git log --name-status HEAD^..HEAD
   ```
   Посмотрите, какие файлы изменились:
   - `requirements.txt`, `package.json` → установить зависимости.
   - `migrations/*.py` → применить миграции.
   - `Dockerfile`, `docker-compose.yml` → пересобрать контейнеры.
   - `static/` или `templates/` с новыми файлами → собрать `collectstatic`.

2. **Проверить зависимости**:
   ```bash
   git diff HEAD^ HEAD requirements.txt
   ```
   Если есть изменения, обновите зависимости.

3. **Проверить миграции**:
   ```bash
   python manage.py showmigrations
   ```
   Если есть неприменённые миграции, выполните:
   ```bash
   python manage.py migrate
   ```

## Работа с конфликтами при `git pull`
Если возник конфликт:
1. Проверить конфликтующие файлы:
   ```bash
   git status
   ```
2. Разрешить конфликты вручную:
   - Откройте файлы, найдите маркеры `<<<<<<<`, `=======`, `>>>>>>>`.
   - Выберите нужные изменения.
3. Добавить разрешённые файлы:
   ```bash
   git add .
   ```
4. Завершить слияние:
   ```bash
   git commit
   ```
5. Продолжить обновление:
   ```bash
   git pull origin main
   ```

## Полезные команды
- **Откатить изменения, если что-то сломалось**:
  ```bash
  git reset --hard HEAD^  # Откатить до предыдущего коммита
  git pull origin main  # Повторить pull
  ```
- **Очистить кэш Docker** (если образы не обновляются):
  ```bash
  docker system prune -a
  docker-compose build --no-cache
  ```
- **Проверить логи сервера**:
  ```bash
  journalctl -u gunicorn -n 100
  docker-compose logs web
  ```
- **Проверить статус сервисов**:
  ```bash
  sudo systemctl status gunicorn nginx
  docker-compose ps
  ```

## Советы
- **Создайте бэкап перед обновлением**:
  ```bash
  tar -czf backup_$(date +%Y%m%d).tar.gz /path/to/project
  pg_dump -U postgres dbname > db_backup_$(date +%Y%m%d).sql
  ```
- **Тестируйте на staging-сервере**:
  - Сначала примените `git pull` на staging, чтобы избежать проблем на продакшене.
- **Используйте CI/CD**:
  - Настройте GitHub Actions или GitLab CI для автоматического деплоя.
- **Логируйте изменения**:
  ```bash
  git pull origin main | tee -a deploy.log
  ```

## Пример полного деплоя (Docker + Django)
```bash
cd /path/to/project
git pull origin main
if git diff HEAD^ HEAD requirements.txt | grep .; then
    docker-compose build
fi
if git diff HEAD^ HEAD migrations/ | grep .; then
    docker-compose exec web python manage.py migrate
fi
docker-compose down
docker-compose up -d
docker-compose exec web python manage.py collectstatic --noinput
```

## Частые ошибки
- **"Your local changes would be overwritten"**:
  Решение:
  ```bash
  git stash  # Сохранить локальные изменения
  git pull origin main
  git stash pop  # Вернуть изменения
  ```
- **"Database migrations conflict"**:
  Проверьте миграции:
  ```bash
  python manage.py makemigrations --check
  ```
  Если есть конфликты, исправьте их вручную в `migrations/`.
- **"Docker container fails to start"**:
  Проверьте логи:
  ```bash
  docker-compose logs web
  ```
  Убедитесь, что `.env` актуален.

Если что-то пошло не так, пишите в поддержку или смотрите документацию на [Git](https://git-scm.com/docs) или [Docker](https://docs.docker.com).