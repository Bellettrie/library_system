from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU
from members.models import Member


@register("members.committees")
class Committees(Component):

    # This component takes one parameter, a date string to show in the template
    def get_context_data(self, members: Member = None):
        return {
            "committees": members.committees.all(),
        }

    template_name = "members/details/committees.html"
