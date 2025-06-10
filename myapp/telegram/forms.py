from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime

class TelegramForm(forms.Form):
    channel_url = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=False,
        label='URL каналов'
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        label='Дата начала'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        label='Дата окончания'
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Дата начала не может быть позже даты окончания.")
            if end_date > datetime.now().date():
                raise ValidationError("Дата окончания не может быть в будущем.")