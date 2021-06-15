from django.db import models

# Create your models here.
class History(models.Model):
    username = models.CharField(max_length=30)
    searchquery = models.CharField(max_length=30)
    platform = models.CharField(max_length=10)
    dateandtime = models.CharField(max_length=40)