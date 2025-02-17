from typing import List

from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU
from lendings.models import Lending
from members.models import Member
from reservations.models import Reservation


@register("reservations.card.Card")
class Card(Component):
    def get_context_data(self, reservation: Reservation, perms, show_member: bool = True):
        code = reservation.item.book_code

        return {
            "lendings": reservation,
            "split_code": code.split("-"),
            "perms": perms,
            "show_member": show_member,
        }

    template_name = "reservations/card/card.html"
