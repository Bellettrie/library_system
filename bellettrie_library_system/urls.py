"""bellettrie_library_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from bellettrie_library_system.views import index
from public_pages.views import view_page
from django.shortcuts import redirect


def redirect_view(request):
    response = redirect('/')
    return response


urlpatterns = [
    path('admin/', admin.site.urls),
    path('members/', include('members.urls')),
    path('works/', include('works.urls')),
    path('lend/', include('lendings.urls')),
    path('config/', include('config.urls')),
    path('inventarisation/', include('inventarisation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('creators/', include('creators.urls')),
    path('series/', include('series.urls')),
    path('pages/', include('public_pages.urls')),
    path('datamining/', include('datamining.urls')),
    path('', view_page('basic', 'home'), name='homepage'),
    path('kickin', view_page('basic', 'kickin'), name='homepage'),
    path('kickin/', view_page('basic', 'kickin'), name='homepage'),
    path('informatie/', redirect_view, name='homepage.old_link'),
    path('konnichiwa/', view_page('konnichiwa', 'home'), name='konnichiwa.home'),
    path('recode/', include('recode.urls')),
    path('book_code/', include('book_code_generation.urls')),
]
