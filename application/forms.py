from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import MovieRequest


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'last_name',
            'first_name',
        ]

class MovieRequestForm(ModelForm):
    class Meta:
        model = MovieRequest
        fields = '__all__'
