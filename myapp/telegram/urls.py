# myapp/telegram/urls.py
from django.urls import path
from . import views

app_name = 'telegram'

urlpatterns = [
    path('', views.telegram_view, name='telegram'),
    path('daily/', views.telegram_daily_view, name='telegram_daily'),
    path('export/', views.export_to_excel, name='export_to_excel'),
    path('get_post_details/', views.get_post_details, name='get_post_details'),
    path('update-category/', views.update_post_category, name='update_category'),
    path('apply-changes/', views.apply_changes, name='apply_changes'),
    path('analytics_dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('export-model/', views.export_model_view, name='export_model'),
]