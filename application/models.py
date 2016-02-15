from django.db import models
import os
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction


class MovieDirectory(models.Model):
    path = models.CharField(max_length=4096)
    last_refresh = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.path


class Movie(models.Model):
    path = models.TextField()
    title = models.CharField(max_length=100)
    plot = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    imdbid = models.CharField(max_length=9, null=True, blank=True)
    poster = models.ImageField(upload_to="posters", null=True, blank=True)

    def path_to_static(self):
        return os.path.join(settings.MEDIA_URL, 'films', os.path.basename(self.path))

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class NewMovieNotification(models.Model):
    movie = models.ForeignKey(Movie)
    user = models.ForeignKey(User)
    read = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return "New movie notification for user %s and movie %s" % (self.user, self.movie)

    @staticmethod
    def notify_all(movie):
        with transaction.atomic():
            for user in User.objects.all():
                NewMovieNotification.objects.create(movie=movie, user=user)


class WatchlistItem(models.Model):
    movie = models.ForeignKey(Movie)
    user = models.ForeignKey(User)

    class Meta:
        unique_together = ('movie', 'user')

    def __str__(self):
        return "Watchlist item %s for user %s" % (self.movie, self.user)
