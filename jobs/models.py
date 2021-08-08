from django.db import models


# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='images', blank=True)
    description = models.TextField(blank=True)
    link = models.URLField(max_length=200)
    telephone_number = models.CharField(max_length=12)

