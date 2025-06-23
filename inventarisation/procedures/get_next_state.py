from works.models import ItemState


def get_next_state_by_action(action: str, prev_state: ItemState) -> (str, str):
    if prev_state.state.is_final_state():
        return prev_state.type, prev_state.reason
    if action == "yes":
        if not prev_state.state.is_available:
            return "AVAILABLE", "Seen during inventarisation"
    elif action == "no":
        if not prev_state.state.is_available:
            return "LOST", "Not seen during inventarisation"
        else:
            return "MISSING", "Not seen during inventarisation"

    return prev_state.type, prev_state.reason
