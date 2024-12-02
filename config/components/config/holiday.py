from django_components import Component, register


@register("config.holiday_table")
class HolidayTable(Component):

    # This component takes one parameter, a date string to show in the template
    def get_context_data(self, holidays=""):
        return {
            "holidays": holidays,
        }
    template_name = "config/holiday_table.html"