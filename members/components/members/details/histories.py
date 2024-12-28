from typing import List

from django_components import Component, register

from members.models import Member


@register("members.current_lendings")
class LendingHistory(Component):
    def get_context_data(self,  member:Member):
        return {

            "member": member
        }

    template_name = "members/details/history_lending.html"
