from django import template
from django.conf import settings
from django.utils.http import urlencode

register = template.Library()


@register.inclusion_tag('public_pages/logo.html', takes_context=True)
def get_logo(context):
    return {'debug': settings.UPSIDE_DOWN, "logo": settings.LIBRARY_IMAGE_URL, "name": settings.LIBRARY_NAME}


@register.inclusion_tag('public_pages/title.html', takes_context=True)
def get_title(context):
    return {'debug': settings.UPSIDE_DOWN, "logo": settings.LIBRARY_IMAGE_URL, "name": settings.LIBRARY_NAME, "description": settings.LIBRARY_DESCRIPTION}
