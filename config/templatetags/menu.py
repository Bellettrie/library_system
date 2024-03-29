from django import template
from django.conf import settings


register = template.Library()


@register.inclusion_tag('config/render_menu_item.html', takes_context=True)
def render_menu_item(context, menu_item, mode):
    request = context['request']

    sub_items = menu_item.rendered_sub_items(request)
    return {'menu': menu_item, 'has_sub_items': len(menu_item.sub_items) > 0, 'sub_items': sub_items, 'request': request, 'mode': mode}


@register.inclusion_tag('config/render_menu.html', takes_context=True)
def render_menu(context, mode, menu_name=None):
    request = context['request']
    lst = []
    for item in settings.GET_MENU():
        if item.permits(request):
            if menu_name is None or item.location == menu_name:
                lst.append(item)
    return {'menu': lst, 'request': request, 'mode': mode}
