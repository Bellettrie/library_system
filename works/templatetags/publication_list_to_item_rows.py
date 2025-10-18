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

    def get_book_code(self):
        return self.item.book_code

    def get_book_code_extension(self):
        return self.item.book_code_extension

    def is_item(self):
        return True


class NoItemRow(Row):
    def __init__(self, publication: Publication, book_code: str):
        super().__init__()
        self.book_code = book_code
        self.publication = publication

    def get_item(self) -> Item:
        return Item(publication=self.publication)

    def get_book_code(self):
        print("HI")
        return self.book_code

    def get_book_code_extension(self):
        return ""

    def is_item(self):
        return False


@register.simple_tag
def get_item_rows_for_publications(publications: List[Publication]):
    rows = []
    for publication in publications:
        if hasattr(publication, 'itemid') and publication.itemid:
            item = Item(publication=publication,
                        book_code_sortable=publication.book_code_sortable,
                        book_code_extension=publication.book_code_extension,
                        book_code=publication.book_code)
            rows.append(ItemRow(item=item))
        else:
            rows.append(NoItemRow(publication=publication, book_code=publication.book_code))
            print(publication.book_code)
    return rows
