from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserForm


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
        elif not userform.has_changed():
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
