from django.conf.urls import url
from . import views
from .models import MoviesFeed

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^watch/(?P<mid>[0-9]+)$', views.watch, name="watch"),
    url('^profile$', views.profile, name="profile"),
    url('^random$', views.random_movie, name="random"),
    url('^rss$', MoviesFeed(), name="rss"),
    url('^regen_key$', views.regen_key, name="regen_key"),
    url('^new_movies$', views.new_movies, name='new_movies'),
    url('^watchlist/add$', views.watchlist_add, name='watchlist_add'),
    url('^watchlist/remove$', views.watchlist_remove, name='watchlist_remove'),
    url('^watchlist/list$', views.watchlist_list, name='watchlist_list'),
    url('^request$', views.movie_request, name='movie_request'),
]
