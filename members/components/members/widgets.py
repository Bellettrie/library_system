# In a file called [project root]/components/calendar/calendar.py
from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU


@register("members.search_input")
class SearchInput(Component):

    # This component takes one parameter, a date string to show in the template
    def get_context_data(self, query=""):
        return {
            "query": query,
        }
    template_name = "members/search.html"