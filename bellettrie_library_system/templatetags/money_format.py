from django import template
from django.utils.http import urlencode

register = template.Library()


@register.simple_tag()
def moneys(amount):
    print(amount)
    return "{} euros".format(amount/100)