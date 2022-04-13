from datetime import datetime

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.views.generic import ListView

from members.models import Member, MembershipPeriod
from utils.get_query_words import get_query_words


class MemberList(PermissionRequiredMixin, ListView):
    permission_required = 'members.view_member'
    model = Member
    template_name = 'member_list.html'
    paginate_by = 50
    def get_queryset(self):  # new
        words = get_query_words(self.request.GET.get("q"))
        return query_members(words, self.request.GET.get('previous', False))


def query_members(words, get_previous=False):
    msps = MembershipPeriod.objects.filter((Q(start_date__isnull=True) | Q(start_date__lte=datetime.now()))
                                           & (Q(end_date__isnull=True) | Q(end_date__gte=datetime.now())))
    if words is None:
        return []
    if len(words) == 0:
        m = Member.objects.filter(is_anonymous_user=False)
        if not get_previous:
            m = m.filter(membershipperiod__in=msps)
        return m

    result_set = None
    for word in words:
        members = Member.objects.filter(Q(name__icontains=word) | Q(nickname__icontains=word))
        if not get_previous:
            members = members.filter(membershipperiod__in=msps)
        if result_set is None:
            result_set = members
        else:
            result_set = result_set & members

    return list(set(result_set))
