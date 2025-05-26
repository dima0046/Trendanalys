# myapp/admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from myapp.telegram.models import TelegramChannel, TelegramPost, ParserLog  # Исправленный импорт

# Снимаем дефолтную регистрацию
admin.site.unregister(User)

# Регистрируем с кастомной конфигурацией (если нужно)
admin.site.register(User, UserAdmin)

@admin.register(TelegramChannel)
class TelegramChannelAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'url')

@admin.register(TelegramPost)
class TelegramPostAdmin(admin.ModelAdmin):
    list_display = ('channel', 'post_id', 'date', 'category')
    list_filter = ('channel', 'category')
    search_fields = ('message',)

@admin.register(ParserLog)
class ParserLogAdmin(admin.ModelAdmin):
    list_display = ('channel', 'start_time', 'status', 'posts_fetched')
    list_filter = ('status',)