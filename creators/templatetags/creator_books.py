from django import template
from django.db.models import Q

from creators.models import Creator
from series.models import Series
from tables.buttons import LendBookButton, ReturnBookButton, IsLentOutStatus, NoItemsButton, NotInAvailableStatus
from tables.columns import BookCodeColumn, TitleColumn, AllAuthorsColumn, ButtonsColumn
from tables.rows import ItemRow
from tables.table import Table
from works.models import Publication, Item, SubWork, Work

# from works.views import ItemRow, BookResult

buttons_list = [
    LendBookButton(),
    ReturnBookButton(),
    IsLentOutStatus(),
    NoItemsButton()
]

register = template.Library()

cols = [BookCodeColumn(), TitleColumn(), AllAuthorsColumn(), ButtonsColumn([NotInAvailableStatus()], ""),
        ButtonsColumn(buttons_list, "")]


@register.inclusion_tag('tables/items_table_xs.html')
def get_creator_books(creator: Creator, perms):
    series = set(Series.objects.filter(creatortoseries__creator=creator))
    series_len = 0
    while series_len < len(series):
        series_len = len(series)
        series = series | set(Series.objects.filter(part_of_series__in=series))

    item_set = set()
    for work in Publication.objects.filter(
            Q(creatortowork__creator=creator) | Q(workinseries__part_of_series__in=series) | Q(workinpublication__work__creatortowork__creator=creator)):
        for item in work.item_set.all():
            item_set.add(item)

    result = []
    for item in item_set:
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
