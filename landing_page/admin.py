from django.contrib import admin

from landing_page import models


# Register your models here.

@admin.register(models.Candle)
class CandleAdmin(admin.ModelAdmin):
    pass


def site(request):
    return None