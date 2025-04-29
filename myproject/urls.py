"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp.views import index
from myapp.views import telegram_view
from myapp.views import export_to_excel
from myapp.views import get_post_details
from myapp.views import update_post_category

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('telegram/', telegram_view, name='telegram'),
    path('export_to_excel/', export_to_excel, name='export_to_excel'),
    path('get_post_details/', get_post_details, name='get_post_details'),
    path('update_post_category/', update_post_category, name='update_post_category'),
]
