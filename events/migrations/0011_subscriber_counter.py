# Generated by Django 4.2.11 on 2024-03-25 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_remove_subscriber_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='counter',
            field=models.IntegerField(default=0),
        ),
    ]
