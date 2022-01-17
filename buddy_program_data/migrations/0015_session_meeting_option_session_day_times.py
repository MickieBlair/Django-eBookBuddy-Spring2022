# Generated by Django 3.2.9 on 2021-12-24 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddy_program_data', '0014_session_meeting_option_slot_letter'),
    ]

    operations = [
        migrations.AddField(
            model_name='session_meeting_option',
            name='session_day_times',
            field=models.ManyToManyField(blank=True, related_name='option_sessions', to='buddy_program_data.Reading_Session_Day_Time'),
        ),
    ]
