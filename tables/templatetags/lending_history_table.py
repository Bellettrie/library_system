from typing import List

from bellettrie_library_system.templatetags.paginator_tag import register
from lendings.models import Lending
from tables.columns import StartDate, LentByColumn, HandinDate
from tables.rows import LendingRow
from tables.table import Table

columns = [StartDate(), LentByColumn(), HandinDate()]


@register.inclusion_tag("tables/items_table.html")
def lending_history_table(lendings: List[Lending], perms):
    rows = []
    for lending in lendings:
        rows.append(LendingRow(lending))
    return {"table": Table(rows, columns), "perms": perms}
