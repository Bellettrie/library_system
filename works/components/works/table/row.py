from typing import List

from django.urls import reverse
from django_components import Component, register, types

from works.models import Item


@register("works.table.Row")
class Row(Component):

    # Renders a table row for a single item.
    # all_authors is used to tell the table to show more than one author for each item (if more are linked)
    # skip_header is used to tell the row to not render the item code column.
    def get_context_data(self, item: Item, all_authors=False, skip_header=False, work=None):
        code = item.book_code
        work = work or item.work
        authors = work.get_deduplicated_authors()
        if not all_authors and len(authors) > 0:
            authors = authors[:1]
        print(work, work.title, item.work.title)
        return {
            "skip_header": skip_header,
            "authors": authors,
            "item": item,
            "work": work,
            "item_work": item.work,
            "split_code": code.split("-"),
        }

    template_name = "works/table/row.html"
