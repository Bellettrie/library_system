from typing import List

from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU
from lendings.models import Lending
from members.models import Member
from works.models import Item


@register("works.table.card.Card")
class Card(Component):
    def get_context_data(self, item: Item, perms, all_authors=False):
        code = item.book_code

        return {
            "all_authors": all_authors,
            "item": item,
            "split_code": code.split("-"),
            "perms": perms,
        }

    template_name = "works/table/card/card.html"
