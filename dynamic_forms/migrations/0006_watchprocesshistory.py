# Generated by Django 5.1.2 on 2024-10-28 10:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynamic_forms', '0005_responseformhistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='WatchProcessHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('watched_at', models.DateTimeField(auto_now_add=True)),
                ('process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='process_watch_histories', to='dynamic_forms.process')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_watch_process_histories', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
