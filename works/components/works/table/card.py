from typing import List

from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU
from lendings.models import Lending
from members.models import Member
from works.models import Item


@register("works.table.Card")
class Card(Component):
    def get_context_data(self, item: Item, all_authors=False):
        code = item.book_code
        authors = item.publication.get_authors()
        if not all_authors:
            authors = authors[:1]
        return {
            "item": item,
            "authors": authors,
            "split_code": code.split("-"),
        }

    template_name = "works/table/card.html"
