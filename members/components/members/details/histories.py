from typing import List

from django_components import Component, register

from lendings.models import Lending
from members.models import Member


@register("members.current_lendings")
class LendingHistory(Component):
    def get_context_data(self, member: Member):

        return {
            "member": member,
            "lendings":Lending.objects.filter(member=member, handed_in=False)
        }

    template_name = "members/details/history_lending.html"
