from typing import List

from bellettrie_library_system.templatetags.paginator_tag import register
from lendings.models import Lending
from tables.buttons import LendingTableReturnButton, ExtendButton
from tables.columns import TitleColumn, AllAuthorsColumn, BookCodeColumn, LentByColumn, FineColumn, ButtonsColumn, \
    HandinDate, StartDate
from tables.table import Table
from tables.rows import LendingRow

cols = [
    BookCodeColumn(),
    TitleColumn(),
    AllAuthorsColumn(),
    (),
    HandinDate(),
    FineColumn(),
    ButtonsColumn([ExtendButton()], "Controls")
]


@register.inclusion_tag('tables/items_table.html')
def current_lendings(lendings: List[Lending], perms):
    rows = []
    for lending in lendings:
        rows.append(LendingRow(lending))
    return {'table': Table(rows, cols), 'perms': perms}



cols_me = [
    BookCodeColumn(),
    TitleColumn(),
    AllAuthorsColumn(),
    StartDate(),
    HandinDate(),
    FineColumn(),
    ButtonsColumn([ExtendButton()], "#")
]


@register.inclusion_tag('tables/items_table.html')
def my_lendings(lendings: List[Lending], perms):
    rows = []
    for lending in lendings:
        rows.append(LendingRow(lending))
    return {'table': Table(rows, cols_me), 'perms': perms}
