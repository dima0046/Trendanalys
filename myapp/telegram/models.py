# myapp/telegram/models.py
from django.db import models
from django.utils import timezone

class TelegramChannel(models.Model):
    url = models.URLField(max_length=1000, unique=True)
    title = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  # Новое поле
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title or self.url

class TelegramPost(models.Model):
    channel = models.ForeignKey(TelegramChannel, on_delete=models.CASCADE, related_name='posts')
    post_id = models.BigIntegerField()
    date = models.DateTimeField()
    message = models.TextField(blank=True, null=True)
    link = models.URLField(max_length=1000)
    views = models.IntegerField(default=0)
    reactions = models.IntegerField(default=0)
    forwards = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    category = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)
    er_post = models.FloatField(default=0.0)
    er_view = models.FloatField(default=0.0)
    vr_post = models.FloatField(default=0.0)
    tr = models.FloatField(default=0.0)
    post_type = models.CharField(max_length=50, default='text')
    subscribers = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('channel', 'post_id')

    def __str__(self):
        return f"Post {self.post_id} from {self.channel.title}"

class ParserLog(models.Model):
    STATUS_CHOICES = (
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('RUNNING', 'Running'),
    )
    channel = models.ForeignKey(TelegramChannel, on_delete=models.CASCADE, related_name='logs')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RUNNING')
    message = models.TextField(blank=True, null=True)
    posts_fetched = models.IntegerField(default=0)

    def __str__(self):
        return f"Log for {self.channel.title} at {self.start_time}"