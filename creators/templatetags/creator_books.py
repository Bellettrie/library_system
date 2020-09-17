from django import template
from django.db.models import Q

from creators.models import Creator
from series.models import Series
from works.models import Publication, Item
from works.views import ItemRow, BookResult

register = template.Library()


@register.inclusion_tag('publication_table/publication_table.html')
def get_creator_books(creator: Creator, perms):

    series = set(Series.objects.filter(creatortoseries__creator=creator))
    series_len = 0
    while series_len < len(series):
        series_len = len(series)
        series = series | set(Series.objects.filter(part_of_series__in=series))

    result = []
    for work in Publication.objects.filter(Q(creatortowork__creator=creator)|Q(workinseries__part_of_series__in=series)):
        it = []
        for item in Item.objects.filter(publication=work):
            it.append(ItemRow(item))

        result.append(BookResult(work, it, item_options=[]))
    return {"perms": perms, "contents": result}
