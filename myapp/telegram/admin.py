# myapp/telegram/admin.py
from django.contrib import admin
from .models import TelegramChannel, TelegramPost, ParserLog

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