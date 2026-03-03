from django_components import Component, register

from lendings.procedures.new_lending import can_lend
from members.models import Member
from utils.time import get_today
from works.models import Item


@register("lendings.buttons.Finalize")
class Finalize(Component):
    template_name = "lendings/buttons/finalize.html"

    def get_context_data(self, item: Item, member: Member, user_permissions, bonus_classes=""):
        is_visible = user_permissions["lendings"]["change_lending"]
        cannot_lend_reason = can_lend(item, member, get_today())
        return {
            "item": item,
            "member": member,
            "is_visible": is_visible,
            "cannot_lend_reason": cannot_lend_reason,
            "bonus_classes": bonus_classes,
        }
