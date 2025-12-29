from django_components import Component

from works.models import Item
from works.models.row_data import RowData


class RowBase(Component):
    def get_context_data(self, row: RowData = None, item: Item = None, all_authors=False):
        if row is None and item is None:
            raise Exception("Item card instantiated without data")
        if row is None:
            row = RowData(item=item)

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
