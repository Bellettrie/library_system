from typing import List

from django.urls import reverse
from django_components import Component, register, types

from works.models import Item
from works.templatetags.publication_list_to_item_rows import RowData


@register("works.table.Row")
class Row(Component):

    # Renders a table row for a single item.
    # all_authors is used to tell the table to show more than one author for each item (if more are linked)
    # skip_header is used to tell the row to not render the item code column.
    def get_context_data(self, row: RowData, all_authors=False, skip_header=False):
        item = row.get_item()
        work = row.get_work()
        series = row.get_series()

        creators = work.get_authors()
        code, extens = row.get_book_code()
        if not all_authors and len(creators) > 0:
            creators = creators[:1]

        return {
            "skip_header": skip_header,
            "creators": creators,
            "item": item,
            "work": work,
            "series": series,
            "split_code": code.split("-"),
            "book_code": code,
            "book_code_extension": extens
        }

    template_name = "works/table/row.html"
