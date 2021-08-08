from django.db import models

# Create your models here.


class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название', default='')
    description = models.TextField(verbose_name='Описание', default='')
    date_start = models.DateTimeField(verbose_name='Дата начала')
    participants_number = models.PositiveSmallIntegerField(verbose_name='Количество участников', default=0)
    is_private = models.BooleanField(verbose_name='Частное', default=False)

    class Meta:
        verbose_name_plural = 'События'
        verbose_name = 'Событие'

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=90, verbose_name='Категория', default='')

    class Meta:
        verbose_name_plural = 'Категории'
        verbose_name = 'Категория'

    def __str__(self):
        return self.title