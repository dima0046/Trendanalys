from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Снимаем дефолтную регистрацию
admin.site.unregister(User)

# Регистрируем с кастомной конфигурацией (если нужно)
admin.site.register(User, UserAdmin)