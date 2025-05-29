from typing import List

from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU
from lendings.models import Lending
from members.models import Member
from works.models import Item

@register("search.searchbox")
class Card(Component):
    def get_context_data(self, selected_tag:str ="", with_tags:bool=True) -> dict:

        return {
            "selected_tag": selected_tag,
            "with_tags": with_tags,
        }

    template_name = "searchbox/searchbox.html"
