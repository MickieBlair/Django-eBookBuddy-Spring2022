# Generated by Django 3.2.9 on 2021-12-21 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buddy_program_data', '0004_response_flag_active'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['for_form__name'], 'verbose_name': 'Question', 'verbose_name_plural': 'Questions'},
        ),
    ]