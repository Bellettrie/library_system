from typing import List

from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU
from lendings.models import Lending
from members.models import Member
from works.models import Item


@register("works.table.row")
class Card(Component):

    # Renders a table row for a single item.
    # all_authors is used to tell the table to show more than one author for each item (if more are linked)
    # skip_header is used to tell the row to not render the item code column.
    def get_context_data(self, item: Item, all_authors=False, skip_header=False):
        code = item.book_code
        authors = item.publication.get_authors()
        if not all_authors and len(authors) > 0:
            authors = authors[:1]
        print(all_authors, authors)
        return {
            "skip_header": skip_header,
            "authors": authors,
            "item": item,
            "split_code": code.split("-"),
        }

    template_name = "works/table/row/row.html"
