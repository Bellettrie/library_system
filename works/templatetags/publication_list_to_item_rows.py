from typing import List
from bellettrie_library_system.templatetags.paginator_tag import register

from works.models import Item, Publication


class Row:
    def __init__(self):
        self.table = None

    def get_item(self) -> Item:
        raise NotImplementedError()

    def is_item(self):
        return True


class ItemRow(Row):
    def __init__(self, item: Item):
        super().__init__()
        self.item = item

    def get_item(self) -> Item:
        return self.item

    def is_item(self):
        return True


class NoItemRow(Row):
    def __init__(self, publication: Publication):
        super().__init__()
        self.publication = publication

    def get_item(self) -> Item:
        return Item(publication=self.publication)

    def is_item(self):
        return False


@register.simple_tag
def get_item_rows_for_publications(publications: List[Publication]):
    rows = []
    for publication in publications:
        its = False
        for item in publication.item_set.all():
            rows.append(ItemRow(item))
            its = True
        if not its:
            rows.append(NoItemRow(publication))
    return rows
