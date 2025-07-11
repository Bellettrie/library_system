from django.urls import reverse
from django_components import Component, register

from members.models import Member


@register("members.details.Committees")
class Committees(Component):

    # Renders the committees that a member is in
    def get_context_data(self, member: Member = None):
        return {
            "committees": member.committees.all(),
        }

    template_name = "members/details/committees.html"
