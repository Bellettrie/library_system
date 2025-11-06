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
    def __init__(self, item: Item):
        super().__init__()
        self.item = item

    def get_item(self) -> Item:
        return self.item

    def is_item(self):
        return True


class NoItemRow(Row):
    def __init__(self, publication: Work):
        super().__init__()
        self.publication = publication

    def get_item(self) -> Item:
        return Item(publication=self.publication)

    def is_item(self):
        return False


@register.simple_tag
def get_item_rows_for_publications(publications: List[Work]):
    rows = []
    idz = list()
    no_items = list()
    for publication in publications:
        if hasattr(publication, 'itemid') and publication.itemid:
            idz.append(publication.itemid)
        else:
            no_items.append(publication)

    for item in Item.objects.filter(pk__in=idz).order_by('book_code_sortable'):
        rows.append(ItemRow(item))
    for pub in no_items:
        rows.append(NoItemRow(pub))
    return rows
