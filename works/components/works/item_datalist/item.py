from typing import List

from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU
from lendings.models import Lending
from members.models import Member
from works.models import Item


@register("works.item_datalist.Item")
class Item(Component):

    def get_context_data(self, item: Item, perms):
        return {
            "item": item,
            "perms": perms
        }

    template_name = "works/item_datalist/item.html"
