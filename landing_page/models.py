from django.db import models

# Create your models here.

class Candle(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    image = models.ImageField(upload_to='images/')
    def __str__(self):
        return self.name

class Upsells(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Upsells"

