from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^watch/(?P<title>.+)$', views.watch, name="watch"),
    url('^profile$', views.profile, name="profile"),
]
