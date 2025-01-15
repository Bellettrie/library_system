from typing import List

from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU
from lendings.models import Lending
from members.models import Member
from works.models import Item


@register("works.info_card")
class Card(Component):

    # Renders the committees that a member is in
    def get_context_data(self, item: Item):
        code = item.book_code

        return {
            "item": item,
            "split_code": code.split("-"),
        }

    template_name = "works/info_card/card.html"
