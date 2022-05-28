from django import template

from works.models import Location

register = template.Library()


@register.inclusion_tag('works/location_search.html')
def get_locations(loc_id, commits=True):
    locations = Location.objects.all()
    if loc_id:
        return {"locations": locations, 'loc_id': int(loc_id), 'commits': commits}
    else:
        return {"locations": locations, 'loc_id': None, 'commits': commits}
