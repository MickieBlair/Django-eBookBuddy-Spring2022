# Generated by Django 3.2.9 on 2022-01-10 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reading_sessions', '0015_user_session_status_all_connected'),
    ]

    operations = [
        migrations.AddField(
            model_name='help_request',
            name='reply',
            field=models.TextField(blank=True, null=True),
        ),
    ]
