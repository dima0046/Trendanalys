# 🧼 Шпаргалка по очистке Docker

## 1️⃣ Безопасная чистка (без удаления активных контейнеров)

> Удаляется только мусор: остановленные контейнеры, висячие образы, неиспользуемые volume и кэш.

```bash
# Удалить остановленные контейнеры
docker container prune

# Удалить неиспользуемые образы (dangling)
docker image prune

# Удалить все неиспользуемые образы
docker image prune -a

# Удалить неиспользуемые volume
docker volume prune

# Удалить неиспользуемые сети
docker network prune

# Очистить всё неиспользуемое сразу (контейнеры, образы, volume, сети)
docker system prune

# То же, но полностью, включая volume и dangling-образы
docker system prune -a --volumes
```

---

## 2️⃣ Полная очистка диска (если `/dev/vda2` забит под завязку)

> Удаляется всё — **все образы, контейнеры, volume, кэш**. Проект нужно будет пересобрать.

```bash
# Остановить все контейнеры
docker stop $(docker ps -aq)

# Удалить все контейнеры
docker rm $(docker ps -aq)

# Удалить все образы
docker rmi $(docker images -q)

# Удалить все volume
docker volume rm $(docker volume ls -q)

# Удалить все сети (не встроенные)
docker network rm $(docker network ls -q)

# Или одной командой — полностью очистить всё
docker system prune -a --volumes
```

> 💡 После этого можно заново собрать проект:
```bash
docker-compose build --no-cache
docker-compose up -d
```

---

## 📦 Дополнительно: как узнать, что занимает место

```bash
# Размер всех docker-объектов
docker system df

# Объём папок в docker
du -sh /var/lib/docker/*

# Установи ncdu для анализа вручную
apt install ncdu
ncdu /
```