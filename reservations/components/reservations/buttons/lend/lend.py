from django_components import Component, register
from lendings.procedures.new_lending import can_lend
from utils.time import get_today


@register("reservations/buttons/lend")
class Button(Component):
    template_name = "reservations/buttons/lend/lend.html"

    def get_context_data(self, reservation, user_member, perms, bonus_classes=""):
        is_visible = True
        if not perms["lendings"]["add_lending"]:
            is_visible = False
        cannot_lend_reason = can_lend(reservation.item, reservation.member, get_today())
        return {
            "is_visible": is_visible,
            "cannot_lend_reason": cannot_lend_reason,
            "reservation": reservation,
            "bonus_classes": bonus_classes,
        }
