from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^watch/(?P<mid>[0-9]+)$', views.watch, name="watch"),
]
