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
import logging

from django.contrib import admin
from django.urls import path, include

from public_pages.views import view_page
from django.shortcuts import redirect
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static


def redirect_view(_):
    response = redirect('/')
    return response


def ok(_):
    logger = logging.getLogger(__name__)
    logger.debug(settings.HOST)
    return HttpResponse("OK from " + settings.HOST + " running version " + settings.VERSION)


urlpatterns = ([
                   path('admin/', admin.site.urls),
                   path('members/', include('members.urls')),
                   path('works/', include('works.urls')),
                   path('lend/', include('lendings.urls')),
                   path('reservations/', include('reservations.urls')),
                   path('config/', include('config.urls')),
                   path('inventarisation/', include('inventarisation.urls')),
                   path('accounts/', include('django.contrib.auth.urls')),
                   path('creators/', include('creators.urls')),
                   path('series/', include('series.urls')),
                   path('pages/', include('public_pages.urls')),
                   path('datamining/', include('datamining.urls')),
                   path('', view_page(settings.STANDARD_PAGE_GROUP, 'home'), name='homepage'),
                   path('kickin/', view_page(settings.STANDARD_PAGE_GROUP, 'kickin'), name='kick'),
                   path('konnichiwa/', view_page('konnichiwa', 'home'), name='konnichiwa.home'),
                   path('recode/', include('recode.urls')),
                   path('book_code/', include('book_code_generation.urls')),

                   # If our service is running, we should return a 200 OK with our liveless checks
                   path('healthz/', ok),
                   path('readyz/', ok),
                   path('livez/', ok),
               ])
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
