import random
from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserForm


def index(request):
    return render(request, 'index.html', {
        'enable_simple_search': True,
    })


def watch(request, title):
    ctx = {
        'movie': get_object_or_404(Movie, title=title),
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


def random_movie(request):
    movies = list(Movie.objects.all())
    try:
        choice = random.choice(movies)
        return redirect('watch', title=choice.title)
    except IndexError:
        return render(request, 'random.html')
