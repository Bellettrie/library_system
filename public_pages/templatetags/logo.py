from django import template
from django.conf import settings
from django.utils.http import urlencode

register = template.Library()


@register.inclusion_tag('public_pages/logo.html', takes_context=True)
def get_logo(context):
    return {'debug': settings.UPSIDE_DOWN}
