from .forms import UserForm, MovieRequestForm
from .models import Movie, NewMovieNotification, WatchlistItem, MovieRequest, MoviesFeed
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
import json
import random


def index(request):
    return render(request, 'index.html', {
        'enable_simple_search': True,
    })


def watch(request, mid):
    try:
        ctx = {
            'movie': get_object_or_404(Movie, pk=mid),
        }
    except MultipleObjectsReturned:
        ctx = {
            'movie': Movie.objects.filter(pk=mid).first(),
        }
    return render(request, 'watch.html', ctx)


@login_required
def profile(request):
    if request.method == "POST":
        userform = UserForm(request.POST, instance=request.user)
        passwordform = PasswordChangeForm(request.user, request.POST)

        error = False
        if userform.has_changed() and userform.is_valid():
            userform.save()
        elif not userform.has_changed():
            userform = UserForm(instance=request.user)
        else:
            error = True

        if passwordform.has_changed() and passwordform.is_valid():
            passwordform.save()
        elif not passwordform.has_changed():
            passwordform = PasswordChangeForm(user=request.user)
        else:
            error = True

        if not error:
            redirect('login')

    else:
        userform = UserForm(instance=request.user)
        passwordform = PasswordChangeForm(user=request.user)

    ctx = {
        'userform': userform,
        'passwordform': passwordform,
    }
    return render(request, 'profile.html', ctx)

@login_required
def new_movies(request):
    ctx = {
        'unread_notifications': [],
        'read_notifications': [],
    }

    with transaction.atomic():
        for notification in NewMovieNotification.objects.filter(user=request.user, read=True)[:10]:
            ctx['read_notifications'].append(notification.movie)
        for notification in NewMovieNotification.objects.filter(user=request.user, read=False):
            ctx['unread_notifications'].append(notification.movie)
            notification.read = True
            notification.save()

    return render(request, 'new_movies.html', ctx)


def random_movie(request):
    movies = list(Movie.objects.all())
    try:
        choice = random.choice(movies)
        return redirect('watch', mid=choice.pk)
    except IndexError:
        return render(request, 'random.html')


@login_required
def watchlist_add(request):
    json_data = json.loads(request.read().decode())
    try:
        movie = Movie.objects.get(pk=json_data['movie'])
        WatchlistItem.objects.create(user=request.user, movie=movie)
        return JsonResponse({'movie': {
            'id': movie.id,
            'title': movie.title,
            'poster': movie.poster.url if movie.poster else '',
            'url': reverse('watch', kwargs={'mid': movie.id}),
        }})
    except Movie.DoesNotExist:
        return JsonResponse({'error': 'Movie does not exists'})
    except IntegrityError:
        return JsonResponse({'error': 'Movie is already in the watchlist'})


@login_required
def watchlist_remove(request):
    json_data = json.loads(request.read().decode())
    try:
        movie = Movie.objects.get(pk=json_data['movie'])
        WatchlistItem.objects.filter(user=request.user, movie=movie).delete()
    except Movie.DoesNotExist:
        pass
    return JsonResponse({})


@login_required
def watchlist_list(request):
    return JsonResponse({
        'movies': [{
            'id': item.movie.id,
            'title': item.movie.title,
            'poster': item.movie.poster.url if item.movie.poster else '',
            'url': reverse('watch', kwargs={'mid': item.movie.id}),
        } for item in WatchlistItem.objects.filter(user=request.user)]
    })

@login_required
def movie_request(request):
    if request.method == 'POST':
        form = MovieRequestForm(request.POST)
        if form.is_valid():
            movie_request = form.save(commit=False)
            movie_request.user = request.user
            movie_request.save()
            return redirect('movie_request')
    else:
        form = MovieRequestForm()

    ctx = {
        'form': form,
        'movie_requests': MovieRequest.objects.all(),
    }
    return render(request, 'request.html', ctx)

@permission_required("application.can_delete_movierequest")
def delete_movie_request(request, pk):
    MovieRequest.objects.filter(pk=pk).delete()
    return redirect('movie_request')

@login_required
def regen_key(request):
    request.user.profile.regen_key()
    return redirect('profile')

