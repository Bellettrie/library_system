from works.models import ItemState

yes_states =  ["AVAILABLE", "BROKEN", "FORSALE", "DISPLAY", "OFFSITE", "FEATURED"]
no_states = ["MISSING", "LOST"]
final_states = ["SOLD"]

def get_next_state_by_action(action: str, prev_state: ItemState) -> (str, str):
    if prev_state.type in final_states:
        return prev_state.type, prev_state.reason
    if action == "yes":
        if prev_state.type in no_states:
            return "AVAILABLE", "Seen during inventarisation"
    elif action == "no":
        if prev_state.type in no_states:
            return "LOST", "Not seen during inventarisation"
        else:
            return "MISSING", "Not seen during inventarisation"

    return prev_state.type, prev_state.reason