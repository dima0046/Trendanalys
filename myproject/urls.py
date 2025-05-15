from django.contrib import admin
from django.urls import path
from myapp.views import index, telegram_view, export_to_excel, apply_changes, update_post_category, export_model_view, get_post_details,analytics_dashboard
from asgiref.sync import async_to_sync

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('telegram/', async_to_sync(telegram_view), name='telegram'),  # Оборачиваем telegram_view
    path('export_to_excel/', export_to_excel, name='export_to_excel'),
    path('get_post_details/', async_to_sync(get_post_details), name='get_post_details'),  # Оборачиваем get_post_details
    path('update_post_category/', update_post_category, name='update_post_category'),
    path('apply_changes/', apply_changes, name='apply_changes'),
    path('export_model/', export_model_view, name='export_model'),
    path('analytics_dashboard/', analytics_dashboard, name='analytics_dashboard'),  # New URL pattern
]