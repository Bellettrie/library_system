from django.urls import reverse
from django_components import Component, register, types

from lendings.procedures.extend import can_extend
from lendings.procedures.new_lending import can_lend, item_can_be_lended
from members.models import Member
from utils.time import get_today
from works.models import Item


@register("lendings/buttons/finalize")
class Button(Component):
    template_name = "lendings/buttons/finalize/finalize.html"

    def get_context_data(self, item: Item, member: Member, perms, bonus_classes=""):
        is_visible = perms["lendings"]["change_lending"]
        cannot_lend_reason = can_lend(item, member, get_today())
        return {
            "item": item,
            "member": member,
            "is_visible": is_visible,
            "cannot_lend_reason": cannot_lend_reason,
            "perms": perms,
            "bonus_classes": bonus_classes,
        }
