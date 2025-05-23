# Django imports
from django.shortcuts import render

# Django users imports
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView

# Forms
from .forms import CustomAuthenticationForm, CustomPasswordChangeForm

# Regular expressions
import re

# Date and time
import time

# Logging
import logging

# Operating system utilities
import os

# Environment variables
from dotenv import load_dotenv

load_dotenv()
api_id = os.getenv("API_ID")  
api_hash = os.getenv("API_HASH")  

# Настройка логирования
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'myapp/index.html')

def custom_logout(request):
    logout(request)
    messages.success(request, "Вы успешно вышли!")
    return redirect('index')

def custom_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.POST.get('next', request.GET.get('next', 'index'))
                messages.success(request, "Вы успешно вошли!")
                return redirect(next_url)
            else:
                messages.error(request, "Неверное имя пользователя или пароль.")
        else:
            messages.error(request, "Ошибка в данных формы.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'myapp/login.html', {'form': form})

def password_change_done(request):
    return render(request, 'myapp/password_change_done.html')

class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'myapp/password_change.html'
    success_url = '/password_change_done/'  # Оставляем как есть, но теперь маршрут будет работать

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Ваш пароль успешно изменён!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Ошибка при смене пароля. Проверьте введённые данные.")
        return self.render_to_response(self.get_context_data(form=form))

def cleanup_temp_data(folder='temp_data', max_age_seconds=86400):
    """
    Удаляет файлы в указанной папке, которые старше max_age_seconds.
    По умолчанию удаляет файлы старше одного дня (86400 секунд).
    """
    now = time.time()
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            file_age = now - os.path.getmtime(file_path)
            if file_age > max_age_seconds:
                os.remove(file_path)
                logger.debug(f"Deleted old file: {file_path}")