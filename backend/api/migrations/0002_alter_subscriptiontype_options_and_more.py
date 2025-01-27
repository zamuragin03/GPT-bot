# Generated by Django 5.1.4 on 2024-12-09 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscriptiontype',
            options={'verbose_name': 'Типы подписок', 'verbose_name_plural': 'Типы подписок'},
        ),
        migrations.AlterModelOptions(
            name='usersubscription',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AddField(
            model_name='subscriptiontype',
            name='price',
            field=models.IntegerField(default=0),
        ),
    ]
