from django.contrib import admin
from .models import Movie, NewMovieNotification, MovieDirectory, WatchlistItem

admin.site.register(Movie)
admin.site.register(NewMovieNotification)
admin.site.register(MovieDirectory)
admin.site.register(WatchlistItem)
