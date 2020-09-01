import datetime
from django import template

from config.menu import my_menu

register = template.Library()


@register.inclusion_tag('render_menu_item.html', takes_context=True)
def render_menu_item(context, menu_item, mode):
    request = context['request']
    print(request)
    sub_items = menu_item.rendered_sub_items(request)
    return {'menu': menu_item, 'has_sub_items': len(menu_item.sub_items) > 0, 'sub_items': sub_items, 'request': request, 'mode': mode}


@register.inclusion_tag('render_menu.html', takes_context=True)
def render_menu(context, mode, menu_name=None):
    request = context['request']
    lst = []
    for item in my_menu:
        if item.permits(request):
            if menu_name is None or item.location == menu_name:
                lst.append(item)
    return {'menu': lst, 'request': request, 'mode': mode}
