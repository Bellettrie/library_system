from django import template
from django.utils.http import urlencode

from components.navbar.menu import menu_with_only_right_permissions, sidebar

register = template.Library()


@register.simple_tag(takes_context=True)
def sidebar_trash(context):
    print(context.get('perms'), len(menu_with_only_right_permissions(sidebar, context.get('perms')))>0)
    perms = context.get('perms', None)
    print(perms)
    if len(menu_with_only_right_permissions(sidebar, perms)) > 0:
        print('style="padding-right: min(.25rem*80,max(100% -(var(--max-w)),0px))"')
        return 'style="padding-right: min(.25rem*80,max(100% - (var(--max-w)),0px))"'
    return ""
