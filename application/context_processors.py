from .models import Movie

def movies(request):
    return {
        'movies': Movie.objects.all()
    }
