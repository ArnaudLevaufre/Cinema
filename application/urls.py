from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^watch/(?P<mid>[0-9]+)$', views.watch, name="watch"),
    url('^profile$', views.profile, name="profile"),
    url('^random$', views.random_movie, name="random"),
    url('^new_movies$', views.new_movies, name='new_movies'),
]
