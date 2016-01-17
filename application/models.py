from django.db import models
import os
from django.conf import settings


class Movie(models.Model):
    path = models.TextField(unique=True)
    title = models.CharField(max_length=100)
    plot = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    imdbid = models.CharField(max_length=9, null=True, blank=True)
    poster = models.ImageField(upload_to="posters", null=True, blank=True)

    def path_to_static(self):
        return os.path.join(settings.MEDIA_URL, 'films', os.path.basename(self.path))

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
