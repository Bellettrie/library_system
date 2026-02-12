from django_components import Component, register

from lendings.procedures.new_lending import item_can_be_lended
from utils.time import get_today
from works.models import Item


@register("lendings.buttons.Lend")
class Lend(Component):
    template_name = "lendings/buttons/lend.html"

    def get_context_data(self, item: Item, user_permissions, bonus_classes=""):
        is_visible = user_permissions["lendings"]["change_lending"]
        cannot_lend_reason = item_can_be_lended(item, get_today())
        return {
            "item": item,
            "is_visible": is_visible,
            "cannot_lend_reason": cannot_lend_reason,
            "bonus_classes": bonus_classes,
        }
