from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from myapp.views import telegram_view, index, export_to_excel, get_post_details, update_post_category, apply_changes, analytics_dashboard, export_model_view, custom_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),  # Домашняя страница
    path('telegram/', telegram_view, name='telegram'),  # Страница Telegram
    path('export/', export_to_excel, name='export_to_excel'),
    path('post-details/', get_post_details, name='post_details'),
    path('update-category/', update_post_category, name='update_category'),
    path('apply-changes/', apply_changes, name='apply_changes'),
    path('analytics/', analytics_dashboard, name='analytics_dashboard'),
    path('export-model/', export_model_view, name='export_model'),
    # Добавляем маршруты для авторизации
    path('login/', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),  # Кастомный вид для выхода
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='myapp/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='myapp/password_change_done.html'), name='password_change_done'),
]