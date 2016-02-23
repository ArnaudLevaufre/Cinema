from django.contrib import admin
from .models import Movie, NewMovieNotification, MovieDirectory, WatchlistItem


class MovieAdmin(admin.ModelAdmin):
    search_fields = ['title']


admin.site.register(Movie, MovieAdmin)
admin.site.register(NewMovieNotification)
admin.site.register(MovieDirectory)
admin.site.register(WatchlistItem)
