from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU


@register("members.search_input")
class SearchInput(Component):
    # The search input for the member page
    def get_context_data(self, query="", previous: bool = False):
        return {
            "query": query,
            "previous": previous,
        }

    template_name = "members/search.html"
