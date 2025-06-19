from inventarisation.procedures.get_next_state import yes_states, no_states, final_states
from works.models import ItemState



class InventarisationRow:
    """
        An InventarisationRow represents all the info required to render one row in the inventarisation
        Args:
            item (Item): The item this row is about
            state (str): the current state of this row: yes, no or skip
            prev_state (ItemState): The state of this item before this inventarisation
            opts_enabled (bool): whether to show the inventarisation_state selector at all.
    """
    def __init__(self, item, state, prev_state, opts_enabled):
        self.item = item
        self.state = state
        self.prev_state = prev_state
        self.opts_enabled = opts_enabled



def get_item_rows( inventarisation, items):
    """
    This function returns a list of inventarisation rows for a given group. A group is a paginated set of items
    """
    rows = []
    for item in items:
        prev = item.get_most_recent_state_not_this_inventarisation(inventarisation)
        enabled = prev.type not in final_states

        try:
            state_in_inventarisation = ItemState.objects.get(item=item, inventarisation=inventarisation)
            if state_in_inventarisation.type in yes_states:
                rows.append(InventarisationRow(item, "yes", prev,enabled))
            elif state_in_inventarisation.type in no_states:
                rows.append(InventarisationRow(item, "no", prev,enabled))
            else:
                rows.append(InventarisationRow(item, "skip", prev, enabled))
        except ItemState.DoesNotExist:
            rows.append(InventarisationRow(item, "skip", prev,enabled))
    return rows
