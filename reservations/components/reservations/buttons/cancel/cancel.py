from django_components import Component, register


@register("reservations/buttons/cancel")
class Button(Component):
    template_name = "reservations/buttons/cancel/cancel.html"

    def get_context_data(self, reservation, user_member, perms, bonus_classes=""):
        is_visible = True
        if reservation.member != user_member and not perms["lendings"]["change_reservation"]:
            is_visible = False

        return {
            "is_visible": is_visible,
            "reservation": reservation,
            "perms": perms,
            "bonus_classes": bonus_classes,
        }
