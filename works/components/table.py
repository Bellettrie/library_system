from django_components import Component, register


@register("item_table")
class ItemTable(Component):
    template_name = "table.html"

    # Item table component
    def get_context_data(self, items):
        return {
            "items": items,
        }
