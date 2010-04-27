from django.db import models

# Create your models here.

class Song(models.Model):
    artist = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    source = models.URLField()