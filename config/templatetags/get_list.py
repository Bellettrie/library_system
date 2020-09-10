from django import template

register = template.Library()


@register.filter
def get_list(dictionary, key):
    return dictionary.getlist(key)


@register.filter
def to_string(string):
    return str(string)
