# Generated by Django 3.2.9 on 2021-12-21 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20211220_1343'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='role',
        ),
        migrations.AddField(
            model_name='customuser',
            name='roles',
            field=models.ManyToManyField(blank=True, related_name='user_roles', to='users.Role'),
        ),
    ]
