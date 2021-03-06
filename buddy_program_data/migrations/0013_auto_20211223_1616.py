# Generated by Django 3.2.9 on 2021-12-23 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddy_program_data', '0012_auto_20211223_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='daily_session',
            name='student_entry_allowed_end',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Student End'),
        ),
        migrations.AlterField(
            model_name='daily_session',
            name='student_entry_allowed_start',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Student In'),
        ),
    ]
