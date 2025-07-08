from typing import List
from bellettrie_library_system.templatetags.paginator_tag import register

from works.models import Item, Work


class Row:
    def __init__(self):
        self.table = None

    def get_item(self) -> Item:
        raise NotImplementedError()

    def is_item(self):
        return True


class ItemRow(Row):
    def __init__(self, item: Item, work: Work):
        super().__init__()
        self.item = item
        self.work = work

    def get_item(self) -> Item:
        return self.item

    def get_work(self):
        return self.work

    def is_item(self):
        return True


class NoItemRow(Row):
    def __init__(self, work: Work):
        super().__init__()
        self.work = work

    def get_item(self) -> Item:
        return Item(work=self.work)

    def get_work(self):
        return self.work

    def is_item(self):
        return False


@register.simple_tag
def get_item_rows_for_publications(works: List[Work]):
    rows = []
    for work in works:
        its = False
        for item in work.get_items():
            rows.append(ItemRow(item, work))
            its = True
        if not its:
            rows.append(NoItemRow(work))
    return rows
