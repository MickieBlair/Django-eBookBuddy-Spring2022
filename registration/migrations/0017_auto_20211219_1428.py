# Generated by Django 3.2.9 on 2021-12-19 19:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0016_auto_20211219_1335'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parent_registration',
            name='device_in_touch',
        ),
        migrations.RemoveField(
            model_name='parent_registration',
            name='full_name_signature',
        ),
        migrations.RemoveField(
            model_name='parent_registration',
            name='messaging_apps',
        ),
        migrations.RemoveField(
            model_name='parent_registration',
            name='other_device_in_touch',
        ),
        migrations.RemoveField(
            model_name='parent_registration',
            name='other_message_app',
        ),
        migrations.RemoveField(
            model_name='parent_registration',
            name='parent_available',
        ),
        migrations.RemoveField(
            model_name='parent_registration',
            name='preferred_contact_language',
        ),
    ]