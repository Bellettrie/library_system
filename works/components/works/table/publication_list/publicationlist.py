from typing import List

from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU
from lendings.models import Lending
from members.models import Member
from works.models import Item, Publication


@register("works.table.publication_list.PublicationList")
class PublicationList(Component):
    # The publication_list component shows an item table for a list of publications.
    # The context data creates dummy Items for Publications without items.
    def get_context_data(self, publications: List[Publication], perms,
                         small_table: bool = False, skip_header=False):
        if small_table:
            btn_bonus_classes = "join-item btn-xs"
        else:
            btn_bonus_classes = "join-item btn-sm"

        items = []
        for publication in publications:
            if publication.item_set.count() == 0:
                it = Item(publication=publication)
                items.append(it)
            else:
                for item in publication.item_set.all():
                    items.append(item)

        return {
            "skip_header": skip_header,
            "items": items,
            "perms": perms,
            "all_authors": True,
            "small_table": small_table,
            "btn_bonus_classes": btn_bonus_classes,
        }

    template_name = "works/table/publication_list/list.html"
