# Generated by Django 4.2.11 on 2024-03-25 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_subscriber_letter_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='sent_letter_count',
            field=models.IntegerField(default=0),
        ),
    ]
