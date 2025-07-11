from django.urls import reverse
from django_components import Component, register
from members.models import Member


@register("members.membership_periods")
class MembershipPeriods(Component):
    # Show the membership periods for one member.
    # It feeds the member_id into the template because this is required for the 'new' button.
    def get_context_data(self, member: Member = None):
        return {
            "member_pk": member.pk,
            "periods": member.get_periods(),
        }

    template_name = "members/details/membership_periods.html"
