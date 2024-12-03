from django_components import Component, register


@register("config.holiday_table")
class HolidayTable(Component):

    def get_context_data(self, holidays=None):
        return {
            "holidays": holidays,
        }
    template_name = "config/holiday_table.html"