# Generated by Django 3.2.6 on 2023-08-06 13:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_alter_event_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='events.category'),
        ),
        migrations.AlterField(
            model_name='event',
            name='features',
            field=models.ManyToManyField(blank=True, related_name='events', to='events.Feature'),
        ),
    ]
