import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находите задачи в приложениях
app.autodiscover_tasks(['myapp.telegram'])
