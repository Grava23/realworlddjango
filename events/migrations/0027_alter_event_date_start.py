# Generated by Django 4.2.11 on 2024-04-11 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0026_remove_event_users_delete_userevent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date_start',
            field=models.DateTimeField(verbose_name='Дата начала'),
        ),
    ]
