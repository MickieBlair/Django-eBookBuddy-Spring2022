# Generated by Django 3.2.9 on 2021-12-21 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0022_auto_20211221_0640'),
    ]

    operations = [
        migrations.AddField(
            model_name='parent_registration',
            name='flagged',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='student_registration',
            name='flagged',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='volunteer_registration',
            name='flagged',
            field=models.BooleanField(default=False),
        ),
    ]