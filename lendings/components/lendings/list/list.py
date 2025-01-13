from typing import List

from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU
from lendings.models import Lending
from members.models import Member


@register("lendings.list.List")
class List(Component):

    # Renders the committees that a member is in
    def get_context_data(self, lendings: List[Lending], perms, show_member: bool = True,
                         small_table: bool = False):
        return {
            "lendings": lendings,
            "perms": perms,
            "show_member": show_member,
            "small_table": small_table,
        }

    template_name = "lendings/list/list.html"
