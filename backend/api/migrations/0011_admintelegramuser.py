# Generated by Django 5.1.4 on 2025-02-20 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_telegramuser_is_banned_userpromocode'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminTelegramUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.BigIntegerField(unique=True)),
                ('username', models.CharField(blank=True, max_length=256, null=True)),
            ],
            options={
                'verbose_name': 'Админ',
                'verbose_name_plural': 'Админы',
            },
        ),
    ]
