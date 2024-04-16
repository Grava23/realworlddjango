from django.db import migrations
from django.core.files.images import ImageFile

def set_default_avatar(apps, schema_editor):
    CustomUser = apps.get_model('events', 'CustomUser')
    default_avatar_path = 'avatars/default_avatar.jpg'  # Путь к файлу с аватаркой по умолчанию

    for user in CustomUser.objects.all():  # Получаем всех пользователей
        with open(default_avatar_path, 'rb') as f:
            user.avatar.save(default_avatar_path, ImageFile(f))
            user.save()

class Migration(migrations.Migration):
    dependencies = [
        ('events', '0018_remove_customuser_date_joined_and_more'),  # Зависимость от предыдущей миграции
    ]

    operations = [
        migrations.RunPython(set_default_avatar),
    ]