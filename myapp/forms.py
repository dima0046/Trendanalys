# myapp/forms.py
from django import forms

class TelegramForm(forms.Form):
    channel_url = forms.CharField(label='URL канала', max_length=1000, widget=forms.TextInput(attrs={'placeholder': 'Введите URL канала'}))
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
