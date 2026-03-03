from typing import List

from django_components import Component, register
from reservations.models import Reservation


@register("reservations.list.List")
class List(Component):
    def get_context_data(self, reservations: List[Reservation], perms, show_member: bool = True,
                         small_table: bool = False, skip_header=False):
        if small_table:
            btn_bonus_classes = "join-item btn-xs"
        else:
            btn_bonus_classes = "join-item btn-sm"
        return {
            "skip_header": skip_header,
            "reservations": reservations,
            "show_member": show_member,
            "small_table": small_table,
            "btn_bonus_classes": btn_bonus_classes,
        }

    template_name = "reservations/list/list.html"
