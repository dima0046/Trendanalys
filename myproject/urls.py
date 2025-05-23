# myproject/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from myapp.views import index, custom_logout, custom_login, CustomPasswordChangeView, password_change_done

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('telegram/', include('myapp.telegram.urls', namespace='telegram')),
    path('login/', custom_login, name='custom_login'),
    path('logout/', custom_logout, name='custom_logout'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change_done/', password_change_done, name='password_change_done'),
]