from django import template
from django.db.models import Q

from book_code_generation import procedures
from creators.models import Creator
from creators.procedures.creator_books import get_books_for_author
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
    item_set = get_books_for_author(creator)

    result = []
    for work in item_set:
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
