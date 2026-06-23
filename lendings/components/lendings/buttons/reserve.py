from django_components import Component, register

from members.models import Member
from reservations.procedures.new_reservation import can_reserve
from utils.time import get_today
from works.models import Item


@register("lendings.buttons.Reserve")
class Reserve(Component):
    template_name = "lendings/buttons/reserve.html"

    def get_context_data(self, item: Item, member: Member, is_lent_out, user_permissions, bonus_classes=""):
        is_visible = user_permissions["lendings"]["change_lending"]
        res = "Not logged in"
        if member:
            res = can_reserve(item, member, get_today())
        for_other = can_reserve(item, Member(), get_today(), with_member_checks=False)
        return {
            "item": item,
            "member": member,
            "is_visible": is_visible,
            "cannot_reserve_reason": res,
            "is_lent_out": is_lent_out,
            "for_other_reason": for_other,
            "bonus_classes": bonus_classes,
        }
