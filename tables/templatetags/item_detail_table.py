from bellettrie_library_system.templatetags.paginator_tag import register
from members.models import Member
from tables.buttons import LendBookButton, ReturnBookButton, IsLentOutStatus, StatusButton, StatusChangeButton, \
    ItemEditButton
from tables.columns import BookCodeColumn, ButtonsColumn, Column, RecodeColumn
from tables.table import Table
from tables.rows import ItemRow, Row


class AnonColumn(Column):
    def __init__(self, name, item_func):
        self.name = name
        self.item_func = item_func

    def get_header(self):
        return self.name

    def render(self, row: Row, perms=None):
        return self.item_func(row, row.get_item(), perms)


@register.inclusion_tag('tables/items_table.html')
def detailed_items(its, member: Member, perms):
    cols = [
        BookCodeColumn(),
        RecodeColumn(),
        AnonColumn("ISBN", lambda row, item, pm: (item.isbn10 or "") + " " + (item.isbn13 or "")),
        AnonColumn("Pages", lambda row, item, pm: item.pages),
        AnonColumn("Year", lambda row, item, pm: item.publication_year),
        ButtonsColumn([
            LendBookButton(),
            ReturnBookButton(),
            IsLentOutStatus(),
        ], "Lending"),
        ButtonsColumn([
            StatusButton(),
        ], "Status"),
        ButtonsColumn([
            StatusChangeButton(),
        ], ""),

    ]
    if "works.change_work" in perms:
        cols.append(ButtonsColumn([
            ItemEditButton()
        ], "Edit"))

    rows = []
    for it in its:
        rows.append(ItemRow(it))
    return {'table': Table(rows, cols), "perms": perms}
