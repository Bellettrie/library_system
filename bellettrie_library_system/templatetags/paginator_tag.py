from django import template
from django.utils.http import urlencode

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = {}
    cget = context['request'].GET
    multikeys = []
    for k in cget.keys():
        if len(cget.getlist(k)) == 1:
            query[k] = cget[k]
        else:
            multikeys.append(k)
    query.update(kwargs)
    multikeys_part = ""
    for key in multikeys:
        for v in cget.getlist(key):
            multikeys_part += "&" + urlencode({key: v})
    return urlencode(query) + multikeys_part


@register.filter('get_value_from_dict')
def get_value_from_dict(dict_data, key):
    """
    usage example {{ your_dict|get_value_from_dict:your_key }}
    """
    if key:
        return dict_data.get(key)
