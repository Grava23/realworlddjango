from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from models import CustomUser

@receiver(post_save, sender=User)
def update_customuser_username(sender, instance, **kwargs):
    try:
        custom_user = CustomUser.objects.get(user=instance)
        custom_user.username = instance.username
        custom_user.save()
    except CustomUser.DoesNotExist:
        pass
