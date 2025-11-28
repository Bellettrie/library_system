from django_components import Component, register

from works.models import Item
from works.models.row_data import RowData


@register("works.table.Card")
class Card(Component):
    def get_context_data(self, row: RowData, all_authors=False):
        item = row.get_item()
        work = row.get_work()
        series = row.get_series()

        creators = work.get_authors()
        code, extens = row.get_book_code()
        if not all_authors and len(creators) > 0:
            creators = creators[:1]

        return {
            "creators": creators,
            "item": item,
            "work": work,
            "series": series,
            "split_code": code.split("-"),
            "book_code": code,
            "book_code_extension": extens
        }

    template_name = "works/table/card.html"
