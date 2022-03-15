from django.contrib import admin
from . import models
# Register your models here.


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Feature)
class FeatureAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Enroll)
class EnrollAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
    pass


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
    pass
