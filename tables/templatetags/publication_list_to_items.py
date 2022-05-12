from typing import List

from bellettrie_library_system.templatetags.paginator_tag import register
from tables.buttons import LendBookButton, IsLentOutStatus, NotInAvailableStatus, ReturnBookButton
from tables.columns import TitleColumn, BookCodeColumn, AllAuthorsColumn, ButtonsColumn
from tables.rows import ItemRow
from tables.table import Table
from works.models import Publication

buttons_list = [
    LendBookButton(),
    ReturnBookButton(),
    IsLentOutStatus(),
]
columns = [BookCodeColumn(), TitleColumn(), AllAuthorsColumn(), ButtonsColumn([NotInAvailableStatus()], ""),
           ButtonsColumn(buttons_list, "Controls")]


@register.inclusion_tag("items_table.html")
def works_table(publications: List[Publication], perms):
    rows = []
    for publication in publications:
        for item in publication.item_set.all():
            rows.append(ItemRow(item))
    return {"table": Table(rows, columns), "perms": perms}
