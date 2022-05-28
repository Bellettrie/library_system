from bellettrie_library_system.templatetags.paginator_tag import register

from reservations.models import Reservation
from tables.buttons import ReservationCancelButton, ReservationLendButton

from tables.columns import TitleColumn, AllAuthorsColumn, BookCodeColumn, ButtonsColumn
from tables.table import Table
from tables.rows import ReservationRow

cols = [
    BookCodeColumn(),
    TitleColumn(),
    AllAuthorsColumn(),
    ButtonsColumn([
        ReservationLendButton(),
        ReservationCancelButton()
    ], "Reservation")
]


@register.inclusion_tag('tables/items_table.html')
def current_reservations():
    rows = []
    for reservation in Reservation.objects.order_by('reserved_on'):
        rows.append(ReservationRow(reservation))
    return {'table': Table(rows, cols)}
