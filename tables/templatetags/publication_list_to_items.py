from typing import List

from bellettrie_library_system.templatetags.paginator_tag import register
from tables.buttons import LendBookButton, IsLentOutStatus, NotInAvailableStatus, ReturnBookButton, NoItemsButton
from tables.columns import TitleColumn, BookCodeColumn, AllAuthorsColumn, ButtonsColumn
from tables.rows import ItemRow, NoItemRow
from tables.table import Table
from works.models import Publication

buttons_list = [
    LendBookButton(),
    ReturnBookButton(),
    IsLentOutStatus(),
    NoItemsButton()
]
columns = [BookCodeColumn(), TitleColumn(), AllAuthorsColumn(), ButtonsColumn([NotInAvailableStatus()], ""),
           ButtonsColumn(buttons_list, "")]


@register.simple_tag
def works_table(publications: List[Publication]):
    rows = []
    for publication in publications:
        its = False
        for item in publication.item_set.all():
            rows.append(ItemRow(item))
            its = True
        if not its:
            rows.append(NoItemRow(publication))
    return rows
