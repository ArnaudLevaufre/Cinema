from django.shortcuts import render, get_object_or_404
from .models import Movie


def index(request):
    ctx = {
        'movies': Movie.objects.all(),
    }
    return render(request, 'index.html', ctx)


def watch(request, mid):
    ctx = {
        'movie': get_object_or_404(Movie, pk=mid),
    }
    return render(request, 'watch.html', ctx)
