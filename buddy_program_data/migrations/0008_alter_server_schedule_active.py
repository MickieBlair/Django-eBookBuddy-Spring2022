# Generated by Django 3.2.9 on 2021-12-23 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddy_program_data', '0007_alter_server_schedule_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server_schedule',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
