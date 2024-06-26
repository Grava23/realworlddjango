# Generated by Django 4.2.11 on 2024-03-19 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_subscriber_customuser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscriber',
            name='email',
        ),
        migrations.RemoveField(
            model_name='subscriber',
            name='letter_count',
        ),
        migrations.RemoveField(
            model_name='subscriber',
            name='sent_letter_count',
        ),
        migrations.AddField(
            model_name='subscriber',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='recipient_email',
            field=models.EmailField(default='', max_length=254),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='subscriber_email',
            field=models.EmailField(default='', max_length=254),
        ),
    ]
