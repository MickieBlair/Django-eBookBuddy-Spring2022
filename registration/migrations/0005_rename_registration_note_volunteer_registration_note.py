# Generated by Django 3.2.9 on 2021-12-16 20:36

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('registration', '0004_auto_20211216_1534'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Registration_Note',
            new_name='Volunteer_Registration_Note',
        ),
    ]
