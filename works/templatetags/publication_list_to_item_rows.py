from typing import List
from bellettrie_library_system.templatetags.paginator_tag import register

from works.models import Item, Work
from works.models.row_data import RowData


@register.simple_tag
def get_item_rows_for_publications(publications: List[Work]) -> List[RowData]:
    rows = []
    for publication in publications:
        if hasattr(publication, 'itemid') and publication.itemid and hasattr(publication, 'book_code') and hasattr(
                publication, 'book_code_extension'):
            item = Item(publication=publication, book_code=publication.book_code,
                        book_code_extension=publication.book_code_extension, id=publication.itemid)
            rows.append(RowData(item=item, work=publication))
        else:
            rows.append(RowData(work=publication))
    return rows
