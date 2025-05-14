from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU
from members.models import Member


@register("members.committees")
class Committees(Component):

    # Renders the committees that a member is in
    def get_context_data(self, member: Member = None):
        return {
            "committees": member.committees.all(),
        }

    template_name = "members/details/committees.html"
