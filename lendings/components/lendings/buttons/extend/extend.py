from django.urls import reverse
from django_components import Component, register, types

from lendings.procedures.extend import can_extend
from utils.time import get_today


@register("lendings/buttons/extend")
class Button(Component):
    template_name = "lendings/buttons/extend/extend.html"

    def get_context_data(self, lending, user_member, perms, bonus_classes=""):
        is_visible =   not lending.handed_in
        if lending.member != user_member and not perms["lendings"]["change_lending"]:
            is_visible = False
        cannot_extend_reason = can_extend(lending, get_today())

        return {
            "is_visible": is_visible,
            "cannot_extend_reason": cannot_extend_reason,
            "lending": lending,
            "perms": perms,
            "bonus_classes": bonus_classes,
        }
