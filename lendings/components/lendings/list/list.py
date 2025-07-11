from typing import List

from django.urls import reverse
from django_components import Component, register, types

from lendings.models import Lending


@register("lendings.list.List")
class List(Component):
    def get_context_data(self, lendings: List[Lending], perms, show_member: bool = True,
                         small_table: bool = False, skip_header=False):
        if small_table:
            btn_bonus_classes = "join-item btn-xs"
        else:
            btn_bonus_classes = "join-item btn-sm"
        return {
            "skip_header": skip_header,
            "lendings": lendings,
            "perms": perms,
            "show_member": show_member,
            "small_table": small_table,
            "btn_bonus_classes": btn_bonus_classes,
        }

    template_name = "lendings/list/list.html"
