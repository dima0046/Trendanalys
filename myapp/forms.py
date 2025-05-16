# myapp/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

class TelegramForm(forms.Form):
    channel_url = forms.CharField(label='URL канала', max_length=1000, widget=forms.TextInput(attrs={'placeholder': 'Введите URL канала'}))
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

# Кастомная форма авторизации (можно использовать стандартную AuthenticationForm без изменений)
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя", widget=forms.TextInput(attrs={'placeholder': 'Введите имя пользователя'}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}))

# Кастомная форма смены пароля (можно использовать стандартную PasswordChangeForm без изменений)
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={'placeholder': 'Введите старый пароль'}))
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={'placeholder': 'Введите новый пароль'}))
    new_password2 = forms.CharField(label="Подтверждение нового пароля", widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердите новый пароль'}))