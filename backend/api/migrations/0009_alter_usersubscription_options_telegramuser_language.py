# Generated by Django 5.1.4 on 2025-01-03 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_usersubscription_created_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usersubscription',
            options={'verbose_name': 'Подписка пользователя', 'verbose_name_plural': 'Подписки пользователей'},
        ),
        migrations.AddField(
            model_name='telegramuser',
            name='language',
            field=models.CharField(default='ru', max_length=10),
        ),
    ]
