from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Category(models.Model):
    title = models.CharField(max_length=90, verbose_name='Категория', default='')

    class Meta:
        verbose_name_plural = 'Категории'
        verbose_name = 'Категория'

    def __str__(self):
        return self.title


class Feature(models.Model):
    title = models.CharField(max_length=200, verbose_name='Характераня черта', default='')

    class Meta:
        verbose_name_plural = 'Характерные черты'
        verbose_name = 'Характерная черта'

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название', default='')
    description = models.TextField(verbose_name='Описание', default='')
    date_start = models.DateTimeField(verbose_name='Дата начала')
    participants_number = models.PositiveSmallIntegerField(verbose_name='Количество участников', default=0)
    is_private = models.BooleanField(verbose_name='Частное', default=False)
    category = models.ForeignKey(Category, verbose_name='Категория', default='')
    features = models.ManyToManyFieldtoFeature(Feature)

    class Meta:
        verbose_name_plural = 'События'
        verbose_name = 'Событие'

    def __str__(self):
        return self.title


class Enroll(models.Model):
    user = models.ForeignKey(User, null=True)
    event = models.ForeignKey(Event, null=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    text = models.TextField(verbose_name='текст отзыва', default='')

    class Meta:
        verbose_name_plural = 'записи на события'
        verbose_name = 'запись на событие'

    # def __str__(self):
    #     return self.title

class  Review(models.Model):
    user = models.ForeignKey(User, null=True)
    event = models.ForeignKey(Event, null=True)
    rate = models.PositiveSmallIntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name_plural = 'отзывы на события'
        verbose_name = 'отзывы на событие'

