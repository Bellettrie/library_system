from typing import List

from django_components import Component, register

from config.models import Holiday


@register("config.holiday_table")
class HolidayTable(Component):

    def get_context_data(self, holidays:List[Holiday]=None):
        return {
            "holidays": holidays,
        }
    template_name = "config/holiday_table.html"