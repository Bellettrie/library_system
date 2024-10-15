# In a file called [project root]/components/calendar/calendar.py
from django_components import Component, register


@register("item_table")
class ItemTable(Component):
    template_name = "table.html"

    # This component takes one parameter, a date string to show in the template
    def get_context_data(self, items):
        return {
            "items": items,
        }
