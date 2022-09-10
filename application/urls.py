from django.urls import re_path
from . import views
from .models import MoviesFeed

urlpatterns = [
    re_path('^$', views.index, name='index'),
    re_path('^watch/(?P<mid>[0-9]+)$', views.watch, name="watch"),
    re_path('^profile$', views.profile, name="profile"),
    re_path('^random$', views.random_movie, name="random"),
    re_path('^rss$', MoviesFeed(), name="rss"),
    re_path('^regen_key$', views.regen_key, name="regen_key"),
    re_path('^new_movies$', views.new_movies, name='new_movies'),
    re_path('^watchlist/add$', views.watchlist_add, name='watchlist_add'),
    re_path('^watchlist/remove$', views.watchlist_remove, name='watchlist_remove'),
    re_path('^watchlist/list$', views.watchlist_list, name='watchlist_list'),
    re_path('^request$', views.movie_request, name='movie_request'),
    re_path('^request/delete/(?P<pk>[0-9]+)$', views.delete_movie_request, name='delete_movie_request'),
]
