from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission, PermissionsMixin
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):
    title = models.CharField(max_length=90, default='', verbose_name='Категория')

    def display_event_count(self):
        return self.events.count()
    display_event_count.short_description = 'Количество событий'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Feature(models.Model):
    title = models.CharField(max_length=90, default='', verbose_name='Свойство')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Свойство события'
        verbose_name_plural = 'Свойства события'


class Event(models.Model):
    FULLNESS_FREE = '1'
    FULLNESS_MIDDLE = '2'
    FULLNESS_FULL = '3'
    FULLNESS_LEGEND_FREE = '<= 50%'
    FULLNESS_LEGEND_MIDDLE = '> 50%'
    FULLNESS_LEGEND_FULL = 'sold-out'
    FULLNESS_VARIANTS = (
        (FULLNESS_FREE, FULLNESS_LEGEND_FREE),
        (FULLNESS_MIDDLE, FULLNESS_LEGEND_MIDDLE),
        (FULLNESS_FULL, FULLNESS_LEGEND_FULL),
    )

    title = models.CharField(max_length=200, default='', verbose_name='Название')
    description = models.TextField(default='', verbose_name='Описание')
    date_start = models.DateTimeField(verbose_name='Дата начала')
    participants_number = models.PositiveSmallIntegerField(default=0, verbose_name='Количество участников')
    is_private = models.BooleanField(default=False, verbose_name='Частное')
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE, related_name='events')
    features = models.ManyToManyField(Feature, related_name='events')
    logo = models.ImageField(upload_to='events/list/', blank=True, null=True)


    @property
    def logo_url(self):
        return self.logo.url if self.logo else f'{settings.STATIC_URL}images/svg-icon/event.svg'
#   logo = models.ImageField(upload_to=get_upload_to_auto, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('events:event_detail', args=[str(self.pk)])

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    def __str__(self):
        return self.title

    def display_features(self):
        return ', '.join([feature.title for feature in self.features.all()])
    display_features.short_description = 'features'

    def rate(self, reviews):
        list_review = []
        count = 0
        for review in reviews:
            list_review.append(review.rate)
            count = count + review.rate
        if len(list_review) == 0:
            rate = 0
        else:
            rate = count / len(list_review)
        #    Считается как среднее значение поля rate среди всех отзывов (модель Review),
        #    связанных с данным событием. Значение должно быть округлено до 1 знака после запятой

        return round(rate, 1)

    def get_enroll_count(self):
        """
        Return number of enrolls for this event.
        """
        return self.enrolls.count()

    def get_places_left(self):
        """
        Return number of free places for this event.
        """
        return int(self.participants_number or 0) - self.get_enroll_count()

    def get_fullness_legend(self, **kwargs):
        """
        Return legend for event's places_left.
        Legend is in the FULLNESS_VARIANTS.

        kwargs may contain the following parameters:
        `places_left`: number of free places for this event (to avoid additional query)
        """
        legend = ''
        if int(self.participants_number or 0) > 0:
            legend = Event.FULLNESS_LEGEND_FREE
            places_left = kwargs.get('places_left', None)
            if places_left is None:
                places_left = self.get_places_left()
            if places_left == 0:
                legend = Event.FULLNESS_LEGEND_FULL
            elif places_left < self.participants_number / 2:
                legend = Event.FULLNESS_LEGEND_MIDDLE
        return legend

    def display_enroll_count(self):
        return self.get_enroll_count()
    display_enroll_count.short_description = 'Количество записей'

    def display_places_left(self):
        places_left = self.get_places_left()
        return f'{places_left} ({self.get_fullness_legend(places_left=places_left)})'
    display_places_left.short_description = 'Осталось мест'


class Review(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='reviews')
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE, related_name='reviews')
    rate = models.PositiveSmallIntegerField(default=0)
    text = models.TextField(max_length=1000, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.rate} - {self.event.title}'

    class Meta:
        verbose_name = 'Отзыв на событие'
        verbose_name_plural = 'Отзывы на события'


class Enroll(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='enrolls')
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE, related_name='enrolls')
    created = models.DateTimeField(auto_now_add=True)
    review = models.OneToOneField(Review, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.event.title} - {self.user}'

    class Meta:
        verbose_name = 'Запись на событие'
        verbose_name_plural = 'Записи на событие'


class CustomUser(AbstractUser):
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default_avatar.png',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    password = models.CharField(max_length=128, default='default_password_value')
    groups = models.ManyToManyField(Group, db_table='events_customuser_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set')
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=30, blank=True)

    def get_absolute_url(self):
        return reverse('user_detail', args=[str(self.pk)])

    @receiver(post_save, sender=User)
    def update_custom_user(sender, instance, **kwargs):
        custom_user, created = CustomUser.objects.get_or_create(user=instance)
        custom_user.username = instance.username
        custom_user.email = instance.email
        custom_user.save()

    def delete(self, *args, **kwargs):
        if self.user:
            self.user.delete()

        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscriber(models.Model):
    subscriber_email = models.EmailField(default='')
    recipient_email = models.EmailField(default='')
    created_at = models.DateTimeField(auto_now=True)
    counter = models.IntegerField(default=0)
    letter_count = models.IntegerField(default=0)
    sent_letter_count = models.IntegerField(default=0)  # Добавляем поле sent_letter_count
    counter = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.subscriber_email


