from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.db import models
from django.db import transaction
from django.db.models.signals import post_save
from django.http import HttpResponse
from django.dispatch import receiver
from django.utils import timezone
from django.core.urlresolvers import reverse
import os
import uuid
import urllib


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


class MovieRequest(models.Model):
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, default=None, null=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return "Movie request for %s" % self.title

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


class Subtitle(models.Model):
    path = models.TextField(null=True, blank=True)
    vtt_file = models.FileField(upload_to="subtitles", null=True, blank=True)
    name = models.TextField()
    movie = models.ForeignKey(Movie, related_name="subtitles")

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.UUIDField(blank=True, null=True)

    def regen_key(self):
        self.api_key = uuid.uuid4()
        self.save()


@receiver(post_save, sender=User)
def create_favorites(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class MoviesFeed(Feed):
    title = "Last movies"
    link = "/rss"

    def __call__(self, request, *args, **kwargs):
        key = request.GET.get('key')
        if not key:
            return HttpResponse(status=401)

        for user in User.objects.all():
            if key == str(user.profile.api_key):
                break
        else:
            return HttpResponse(status=401)
        return super().__call__(request, *args, **kwargs)

    def items(self):
        return Movie.objects.order_by('-created')[:25]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        if item.poster:
            return "<div><img src=\"{}\"/><p>{}</p></div>".format(urllib.parse.urljoin(settings.DOMAIN, item.poster.url), item.plot)
        return item.plot

    def item_link(self, item):
        return urllib.parse.urljoin(settings.DOMAIN, reverse('watch', kwargs={'mid': item.id}))

    def item_pubdate(self, item):
        return item.created

