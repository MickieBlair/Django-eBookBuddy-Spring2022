# Generated by Django 3.2.9 on 2022-01-02 18:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0014_student_match_profile_scheduled_slots'),
        ('reading_sessions', '0012_auto_20220101_0838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match_session_status',
            name='sch_match',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sch_match_status', to='matches.scheduled_match'),
        ),
    ]
