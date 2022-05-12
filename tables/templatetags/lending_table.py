from bellettrie_library_system.templatetags.paginator_tag import register
from lendings.models import Lending
from tables.buttons import LendingTableReturnButton
from tables.columns import TitleColumn, AllAuthorsColumn, BookCodeColumn, LentByColumn, FineColumn, ButtonsColumn
from tables.table import Table
from tables.rows import LendingRow

cols = [
    BookCodeColumn(),
    TitleColumn(),
    AllAuthorsColumn(),
    LentByColumn(),
    FineColumn(),
    ButtonsColumn([LendingTableReturnButton()], "Return")
]


@register.inclusion_tag('items_table.html')
def current_lendings(perms):
    rows = []
    for lending in Lending.objects.filter(handed_in=False):
        rows.append(LendingRow(lending))
    return {'table': Table(rows, cols)}
