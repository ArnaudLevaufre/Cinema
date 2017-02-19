from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import reverse

class AccessMiddleware:
    def process_request(self, request):
        if request.path in [reverse('login'), reverse('rss')]:
            return

        if settings.LOGIN_REQUIRED and not request.user.is_authenticated():
            return redirect_to_login(request.path, reverse('login'))
