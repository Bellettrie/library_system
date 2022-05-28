from django import template
from django.db.models import Q

from creators.models import Creator
from series.models import Series
from tables.columns import BookCodeColumn, TitleColumn, AllAuthorsColumn
from tables.rows import ItemRow
from tables.table import Table
from works.models import Publication, Item

# from works.views import ItemRow, BookResult

register = template.Library()

cols = [BookCodeColumn(), TitleColumn(), AllAuthorsColumn()]


@register.inclusion_tag('tables/items_table.html')
def get_creator_books(creator: Creator, perms):
    series = set(Series.objects.filter(creatortoseries__creator=creator))
    series_len = 0
    while series_len < len(series):
        series_len = len(series)
        series = series | set(Series.objects.filter(part_of_series__in=series))

    result = []
    for work in Publication.objects.filter(
            Q(creatortowork__creator=creator) | Q(workinseries__part_of_series__in=series)):
        for item in work.item_set.all():
            result.append(ItemRow(item))
    result.sort(key=lambda r: r.get_item().book_code_sortable)

    return {"perms": perms, "table": Table(result, cols)}


def before_last_dash(my_string: str):
    return "-".join(my_string.split("-")[:-1])


def num_get(my_string: str):
    return my_string.split("-")[-2]


@register.inclusion_tag('creators/single_line_description.html')
def get_creator_name(author: Creator):
    return {"author": author}


register.filter('before_last_dash', before_last_dash)
register.filter('num_get', num_get)
