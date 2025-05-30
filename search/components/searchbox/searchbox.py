from django_components import Component, register


@register("search.searchbox")
class Card(Component):
    def get_context_data(self, selected_tag: str = "", with_tags: bool = True) -> dict:
        return {
            "selected_tag": selected_tag,
            "with_tags": with_tags,
        }

    template_name = "searchbox/searchbox.html"
