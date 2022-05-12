from bellettrie_library_system.templatetags.paginator_tag import register
from lendings.models import Lending
from members.models import Member
from reservations.models import Reservation
from tables.columns import TitleColumn, AllAuthorsColumn, BookCodeColumn, ButtonsColumn, FineColumn
from tables.table import Table
from tables.rows import LendingRow, ReservationRow

cols = [BookCodeColumn(),
        TitleColumn(),
        AllAuthorsColumn(),
        AllAuthorsColumn(),
        ButtonsColumn([], "Return")
        ]


@register.inclusion_tag('items_table.html')
def member_current_reservations(member: Member):
    rows = []
    for reservation in Reservation.objects.filter(member=member):
        rows.append(ReservationRow(reservation))
    return {'table': Table(rows, cols)}


@register.inclusion_tag('items_table.html')
def current_reservations():
    rows = []
    for reservation in Reservation.objects.all():
        rows.append(ReservationRow(reservation))
    return {'table': Table(rows, cols)}
