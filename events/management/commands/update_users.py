from django.core.management.base import BaseCommand
from events.models import User, CustomUser

class Command(BaseCommand):
    help = 'Update users from User model to CustomUser model'

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            custom_user, created = CustomUser.objects.get_or_create(
                user_id=user.id,
                defaults={
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    # Добавьте другие поля, которые нужно скопировать
                }
            )
            if not created:
                custom_user.username = user.username
                custom_user.email = user.email
                custom_user.first_name = user.first_name
                custom_user.last_name = user.last_name
                # Обновите другие поля, если необходимо
                custom_user.save()