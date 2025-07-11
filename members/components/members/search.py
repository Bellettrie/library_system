from django.urls import reverse
from django_components import Component, register, types


@register("members.search_input")
class SearchInput(Component):
    # The search input for the member page
    def get_context_data(self, query="", previous: bool = False, myUrl="/members"):
        return {
            "myUrl": myUrl,
            "query": query,
            "previous": previous,
        }

    template_name = "members/search.html"
