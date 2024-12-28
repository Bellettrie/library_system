from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU


@register("members.membership_periods")
class MembershipPeriods(Component):

    # This component takes one parameter, a date string to show in the template
    def get_context_data(self, members=""):
        return {
            "members": members,
        }

    template_name = "members/details/membership_periods.html"
