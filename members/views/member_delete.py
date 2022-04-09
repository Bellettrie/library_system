from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from members.models import Member, MembershipPeriod
from mail.models import MailLog


@transaction.atomic
@permission_required('members.delete_member')
def delete_member(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html', {'what': "delete member with name " + member.name})
    member = get_object_or_404(Member, pk=member_id)
    MembershipPeriod.objects.filter(member=member).delete()
    anonymous_members = list(Member.objects.filter(is_anonymous_user=True))
    member.destroy(MailLog.objects.filter(member=member), 'member', anonymous_members, False)
    member.delete()

    return HttpResponseRedirect(reverse('members.list'))