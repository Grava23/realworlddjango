# Generated by Django 4.2.11 on 2024-03-25 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_subscriber_counter'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='letter_count',
            field=models.IntegerField(default=0),
        ),
    ]
