from typing import List

from bellettrie_library_system.templatetags.paginator_tag import register
from members.models import Member
from tables.buttons import IsLentOutStatus, FinalizeLendingButton
from tables.columns import Column, TitleColumn, BookCodeColumn, AllAuthorsColumn, ButtonsColumn
from tables.rows import Row, ItemRow
from tables.table import Table
from works.models import Publication


@register.inclusion_tag("tables/items_table.html")
def works_table_for_member(publications: List[Publication], perms, member: Member):
    rows = []
    for publication in publications:
        for item in publication.item_set.all():
            rows.append(ItemRow(item))
    columns: List[Column] = [BookCodeColumn(), TitleColumn(), AllAuthorsColumn(), ButtonsColumn(
        [
            IsLentOutStatus(),
            FinalizeLendingButton(member),
        ], "Controls"
    )]
    return {"table": Table(rows, columns), "perms": perms}
