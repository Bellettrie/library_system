from typing import List

from django.urls import reverse
from django_components import Component, register, types

from works.models import Item


@register("works.table.standard_card.Card")
class Card(Component):
    def get_context_data(self, item: Item, perms) -> dict:
        code = item.book_code
        authors = item.publication.get_authors()

        authors = authors[:1]
        return {
            "item": item,
            "authors": authors,
            "split_code": code.split("-"),
        }

    template_name = "works/table/standard_card/card.html"
