from random import random

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from bellettrie_library_system.base_settings import GET_MENU

register = template.Library()


@register.simple_tag
def menu_data(location, perms):
    menu = GET_MENU()
    result = []
    for item in menu:
        if item.location != location:
            continue
        if (not item.permission) or item.permission in perms:
            result.append(item)
            if item.sub_items is None:
                continue
            for subItem in item.sub_items:
                if subItem.permission and not subItem.permission in perms:
                    item.sub_items.remove(subItem)
    return result
