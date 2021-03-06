# Generated by Django 3.2.9 on 2021-12-21 11:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('buddy_program_data', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Response_Flag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flag_condition', models.CharField(blank=True, max_length=255, null=True)),
                ('action', models.CharField(blank=True, max_length=255, null=True)),
                ('comment', models.TextField(blank=True, max_length=2000, null=True)),
                ('on_question', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='question_flag', to='buddy_program_data.question')),
            ],
            options={
                'verbose_name': 'Response Flag',
                'verbose_name_plural': 'Response Flags',
                'ordering': ['id'],
            },
        ),
    ]
