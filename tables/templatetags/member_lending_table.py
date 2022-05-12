from bellettrie_library_system.templatetags.paginator_tag import register
from lendings.models import Lending
from members.models import Member
from tables.buttons import LendingTableReturnButton
from tables.columns import TitleColumn, AllAuthorsColumn, BookCodeColumn, FineColumn, ButtonsColumn
from tables.table import Table
from tables.rows import LendingRow

cols = [
    BookCodeColumn(),
    TitleColumn(),
    AllAuthorsColumn(),
    FineColumn(),
    ButtonsColumn([LendingTableReturnButton()], "Return")
]

@register.inclusion_tag('items_table.html')
def member_current_lendings(member: Member):
    rows = []
    for lending in Lending.objects.filter(handed_in=False, member=member):
        rows.append(LendingRow(lending))
    return {'table': Table(rows, cols)}
