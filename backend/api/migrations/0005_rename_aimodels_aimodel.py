# Generated by Django 5.1.4 on 2024-12-16 13:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_remove_actiontype_open_ai_name_aimodels_open_ai_name'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AIModels',
            new_name='AIModel',
        ),
    ]
