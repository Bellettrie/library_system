from bellettrie_library_system.templatetags.paginator_tag import register
from members.models import Member
from reservations.models import Reservation
from tables.buttons import ReservationLendButton, ReservationCancelButton
from tables.columns import TitleColumn, AllAuthorsColumn, BookCodeColumn, ButtonsColumn
from tables.table import Table
from tables.rows import ReservationRow
from typing import List

cols = [BookCodeColumn(),
        TitleColumn(),
        AllAuthorsColumn(),
        AllAuthorsColumn(),
        ButtonsColumn([ReservationLendButton(),
                       ReservationCancelButton()], "Return")
        ]


@register.inclusion_tag('tables/items_table.html')
def member_current_reservations(member: Member):
    rows = []
    for reservation in Reservation.objects.filter(member=member):
        rows.append(ReservationRow(reservation))
    return {'table': Table(rows, cols)}


@register.inclusion_tag('tables/items_table.html')
def current_reservations():
    rows = []
    for reservation in Reservation.objects.all():
        rows.append(ReservationRow(reservation))
    return {'table': Table(rows, cols)}


@register.inclusion_tag('tables/items_table.html')
def my_reservations(reservations: List[Reservation], perms):
    rows = []
    for reservation in reservations:
        rows.append(ReservationRow(reservation))
    return {'table': Table(rows, cols), 'perms': perms}
