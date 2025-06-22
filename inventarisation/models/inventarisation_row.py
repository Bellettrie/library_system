class InventarisationRow:
    """
        An InventarisationRow represents all the info required to render one row in the inventarisation
        Args:
            item (Item): The item this row is about
            prev_state (ItemState): The state of this item before this inventarisation
            current_state (ItemState): the current state of this row (optional)
            option_filled: the data put in the form
    """

    def __init__(self, item, prev_state, current_state):
        self.item = item
        self.current_state = current_state
        self.prev_state = prev_state

        # We refill the form if it wasn't filled in
        option_filled = "skip"
        if current_state:
            if prev_state.state.next_yes_state_name == current_state.type:
                option_filled = "yes"
            elif prev_state.state.next_no_state_name == current_state.type:
                option_filled = "no"

        self.opts_enabled = not prev_state.state.is_final_state()
        self.option_filled = option_filled
