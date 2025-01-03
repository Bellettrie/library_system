from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from members.models import Member
from members.permissions import MEMBERS_VIEW


@transaction.atomic
@permission_required('auth.delete_user')
def delete_user(request, member_id, hx_enabled=False):
    if request.GET.get("sure", False):
        member = get_object_or_404(Member, pk=member_id)
        user = member.user
        member.user = None
        member.save()
        user.delete()
        if hx_enabled:
            return HttpResponse(status=209, headers={"HX-Redirect": "true"})
        return HttpResponseRedirect(reverse(MEMBERS_VIEW, args=(member.pk, 0,)))

    # Not sure yet
    templ = 'users/delete.html'
    if hx_enabled:
        templ = 'users/delete_hx.html'
    member = get_object_or_404(Member, pk=member_id)
    return render(request, templ, {'member': member, 'member_user': member.user})
