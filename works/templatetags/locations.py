from django import template
from django.db.models import Q

from creators.models import Creator
from series.models import Series
from works.models import Publication, Item, Location
from works.views import ItemRow, BookResult

register = template.Library()


@register.inclusion_tag('location_search.html')
def get_locations(loc_id, commits=True):
    locations = Location.objects.all()
    if loc_id:
        return {"locations": locations, 'loc_id': int(loc_id), 'commits': commits}
    else:
        return {"locations": locations, 'loc_id': None, 'commits': commits}
