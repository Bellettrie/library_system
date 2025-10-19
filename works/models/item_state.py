from datetime import datetime

from django.db import models
from django.db.models import CASCADE, PROTECT

from inventarisation.models import Inventarisation
from works.models.item import Item


class ItemStateType:
    AVAILABLE = "AVAILABLE"
    FEATURED = "FEATURED"
    MISSING = "MISSING"
    LOST = "LOST"
    BROKEN = "BROKEN"
    OFFSITE = "OFFSITE"
    DISPLAY = "DISPLAY"
    FORSALE = "FORSALE"
    SOLD = "SOLD"

    def __init__(self, state_name, state_description, is_available, next_yes_state_name, next_no_state_name):
        self.state_name = state_name
        self.state_description = state_description
        self.is_available = is_available
        self.next_yes_state_name = next_yes_state_name
        self.next_no_state_name = next_no_state_name

    def is_final_state(self):
        return self.state_name == self.next_yes_state_name == self.next_no_state_name


def get_item_states():
    return \
        [
            ItemStateType(ItemStateType.AVAILABLE, "Available", True, ItemStateType.AVAILABLE, ItemStateType.MISSING),
            ItemStateType(ItemStateType.MISSING, "Missing", False, ItemStateType.AVAILABLE, ItemStateType.LOST),
            ItemStateType(ItemStateType.LOST, "Lost", False, ItemStateType.AVAILABLE, ItemStateType.LOST),
            ItemStateType(ItemStateType.BROKEN, "Broken", False, ItemStateType.BROKEN, ItemStateType.MISSING),
            ItemStateType(ItemStateType.OFFSITE, "Off-Site", False, ItemStateType.OFFSITE, ItemStateType.MISSING),
            ItemStateType(ItemStateType.DISPLAY, "On Display", False, ItemStateType.DISPLAY, ItemStateType.MISSING),
            ItemStateType(ItemStateType.FEATURED, "Featured", True, ItemStateType.FEATURED, ItemStateType.MISSING),
            ItemStateType(ItemStateType.SOLD, "Sold", False, ItemStateType.SOLD, ItemStateType.SOLD),
            ItemStateType(ItemStateType.FORSALE, "For Sale", True, ItemStateType.FORSALE, ItemStateType.MISSING),
        ]


def get_state(name):
    for state in get_item_states():
        if state.state_name == name:
            return state
    return None


def is_item_state_available(name):
    return get_state(name).is_available


def get_available_states():
    result = []
    for state in get_item_states():
        if state.is_available():
            result.append(state)
    return result


def get_itemstate_choices():
    rez = []
    for state in get_item_states():
        rez.append((state.state_name, state.state_description))

    return rez

class ItemState(models.Model):
    CHOICES = get_itemstate_choices()
    item = models.ForeignKey(Item, on_delete=CASCADE)
    date_time = models.DateTimeField(default=datetime.now)
    type = models.CharField(max_length=64, choices=CHOICES)
    reason = models.TextField(blank=True)
    inventarisation = models.ForeignKey(Inventarisation, null=True, blank=True, on_delete=PROTECT)

    @property
    def state(self):
        return get_state(self.type)

    def __str__(self):
        return self.type
