from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse


class AccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in [reverse('login'), reverse('rss')]:
            return self.get_response(request)

        if settings.LOGIN_REQUIRED and not request.user.is_authenticated:
            return redirect_to_login(request.path, reverse('login'))

        return self.get_response(request)
