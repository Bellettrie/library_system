from bellettrie_library_system.templatetags.paginator_tag import register
from lendings.models import Lending
from members.models import Member
from tables.buttons import LendingTableReturnButton, ExtendButton
from tables.columns import TitleColumn, AllAuthorsColumn, BookCodeColumn, FineColumn, ButtonsColumn, HandinDate
from tables.table import Table
from tables.rows import LendingRow

cols = [
    BookCodeColumn(),
    TitleColumn(),
    AllAuthorsColumn(),
    HandinDate(),
    FineColumn(),
    ButtonsColumn([LendingTableReturnButton(), ExtendButton()], "Return")
]


@register.inclusion_tag('tables/items_table.html')
def member_current_lendings(member: Member):
    rows = []
    for lending in Lending.objects.filter(handed_in=False, member=member):
        rows.append(LendingRow(lending))
    return {'table': Table(rows, cols)}
