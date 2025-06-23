from inventarisation.models import InventarisationRow
from works.models import ItemState


def get_item_rows(inventarisation, items):
    """
    This function returns a list of inventarisation rows for a given group. A group is a paginated set of items
    """
    rows = {}
    for item in items:
        prev = item.get_most_recent_state_not_this_inventarisation(inventarisation)

        try:
            state_in_inventarisation = ItemState.objects.get(item=item, inventarisation=inventarisation)
            rows[item.pk] = InventarisationRow(item, prev, state_in_inventarisation)
        except ItemState.DoesNotExist:
            rows[item.pk] = InventarisationRow(item, prev, None)
    return rows
