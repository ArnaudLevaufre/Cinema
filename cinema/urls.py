"""cinema URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.urls import re_path, include
from django.conf import settings
from django.conf.urls.static import  static
from django.contrib.auth import views as auth_views
from django.contrib import admin

urlpatterns = [
    re_path('login/', auth_views.LoginView.as_view(template_name='login.html', extra_context={'login_required': settings.LOGIN_REQUIRED}), name='login'),
    re_path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    re_path('^', include('application.urls')),
    re_path('^admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
