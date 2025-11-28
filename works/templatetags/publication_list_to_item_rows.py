from typing import List
from bellettrie_library_system.templatetags.paginator_tag import register

from works.models import Item, Work
from works.models.row_data import RowData


@register.simple_tag
def get_item_rows_for_publications(publications: List[Work]) -> List[RowData]:
    item_ids_for_publications = set()
    for publication in publications:
        if hasattr(publication, 'itemid') and publication.itemid:
            item_ids_for_publications.add(publication.itemid)

    items = Item.objects.filter(id__in=item_ids_for_publications)
    item_map = {}
    for item in items:
        item_map[item.id] = item

    result = []
    for publication in publications:
        row_item = None
        if hasattr(publication, 'itemid'):
            row_item = item_map.get(publication.itemid, None)
        result.append(RowData(item=row_item, work=publication))

    return result
