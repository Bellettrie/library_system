from django_components import Component, register

from works.models import Item
from works.templatetags.publication_list_to_item_rows import RowData


@register("works.table.Card")
class Card(Component):
    def get_context_data(self, row: RowData, all_authors=False):
        item = row.item
        work = row.work
        series = row.series
        if work is None:
            work = item.publication

        creators = work.get_authors()

        if series is None:
            series = work.as_series()

        code = ""
        code_extension = ""
        if item:
            code = item.book_code
            code_extension = item.book_code_extension
        elif series:
            code = series.book_code

        if not all_authors and len(creators) > 0:
            creators = creators[:1]

        if not series and not item:
            code = "not in collection"
        return {
            "creators": creators,
            "item": item,
            "work": work,
            "series": series,
            "split_code": code.split("-"),
            "book_code": code,
            "book_code_extension": code_extension
        }

    template_name = "works/table/card.html"
