# Generated by Django 4.2.15 on 2024-09-03 20:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.BigIntegerField(verbose_name='Идентификатор телеграм чата')),
                ('comment', models.CharField(max_length=255, verbose_name='Комментарий')),
            ],
            options={
                'verbose_name': 'Чат',
                'verbose_name_plural': 'Чаты',
                'db_table': 'chat',
            },
        ),
        migrations.CreateModel(
            name='System',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('provider', models.CharField(max_length=255, verbose_name='Провайдер')),
            ],
            options={
                'verbose_name': 'Система',
                'verbose_name_plural': 'Системы',
                'db_table': 'system',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaign_id', models.BigIntegerField(verbose_name='Идентификатор кампании')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('login', models.EmailField(max_length=254, verbose_name='Логин')),
                ('balance', models.BigIntegerField(verbose_name='Баланс')),
                ('threshold', models.BigIntegerField(verbose_name='Порог')),
                ('system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='projects.system', verbose_name='Айди системы')),
            ],
            options={
                'verbose_name': 'Проект',
                'verbose_name_plural': 'Проекты',
                'db_table': 'project',
            },
        ),
    ]
