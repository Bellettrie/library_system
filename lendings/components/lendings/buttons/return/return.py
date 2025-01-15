from django.urls import reverse
from django_components import Component, register, types

from lendings.procedures.extend import can_extend
from utils.time import get_today


@register("lendings/buttons/return")
class Button(Component):
    template_name = "lendings/buttons/return/return.html"

    def get_context_data(self, lending, user_member, perms, bonus_classes=""):
        is_visible =   not lending.handed_in
        if not perms["lendings"]["change_lending"]:
            is_visible = False

        return {
            "is_visible": is_visible,
            "lending": lending,
            "perms": perms,
            "bonus_classes": bonus_classes,
        }
