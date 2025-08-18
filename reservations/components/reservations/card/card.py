from django_components import Component, register
from reservations.models import Reservation


@register("reservations.card.Card")
class Card(Component):
    def get_context_data(self, reservation: Reservation, perms, show_member: bool = True):
        code = reservation.item.book_code

        return {
            "reservation": reservation,
            "split_code": code.split("-"),
            "perms": perms,
            "show_member": show_member,
        }

    template_name = "reservations/card/card.html"
