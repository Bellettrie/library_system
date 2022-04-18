from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView

from members.models import Member


class AnonMemberList(PermissionRequiredMixin, ListView):
    permission_required = 'members.view_member'
    model = Member
    template_name = 'member_anonymisable.html'
    paginate_by = 50
