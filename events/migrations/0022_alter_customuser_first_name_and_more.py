from django.db import migrations, models
from events.models import CustomUser
from django.contrib.auth.models import User

def sync_custom_user_data(apps, schema_editor):
    for user in User.objects.all():
        custom_user, created = CustomUser.objects.get_or_create(user=user)
        custom_user.email = user.email
        custom_user.first_name = user.first_name
        custom_user.username = user.username
        custom_user.last_name = user.last_name
        # Добавьте другие поля, которые необходимо синхронизировать
        custom_user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('events', '0021_merge_20240408_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.RunPython(sync_custom_user_data)
    ]


