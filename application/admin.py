from django.contrib import admin
from .models import Movie, NewMovieNotification

admin.site.register(Movie)
admin.site.register(NewMovieNotification)
