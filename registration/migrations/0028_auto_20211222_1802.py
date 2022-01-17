# Generated by Django 3.2.9 on 2021-12-22 23:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('registration', '0027_delete_registration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parent_registration',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='parent_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='staff_registration',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='staff_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='student_registration',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='student_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='volunteer_registration',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='vol_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
