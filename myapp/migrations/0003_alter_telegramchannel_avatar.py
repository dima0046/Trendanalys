# Generated by Django 5.1.1 on 2025-05-28 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_telegramchannel_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramchannel',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
    ]
