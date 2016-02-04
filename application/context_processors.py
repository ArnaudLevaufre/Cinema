from .models import Movie, NewMovieNotification

def movies(request):
    return {
        'movies': Movie.objects.all()
    }

def new_movie_notifications(request):
    if not request.user.is_authenticated():
        return {}

    return {
        'new_movie_notifications': NewMovieNotification.objects.filter(user=request.user, read=False).count() > 0
    }
