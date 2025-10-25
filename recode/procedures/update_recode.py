from recode.models import Recode
from works.models import Item


def update_recode_for_item(item: Item, book_code: str, book_code_extension: str, apply: bool = False):
    Recode.objects.filter(item=item).delete()
    if apply or (
            item.book_code == book_code and item.book_code_extension == book_code_extension):
        item.book_code = book_code
        item.book_code_extension = book_code_extension
        item.save()
    else:
        Recode.objects.create(item=item, book_code=book_code, book_code_extension=book_code_extension)
