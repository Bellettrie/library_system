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
    member = get_object_or_404(Member, pk=member_id)
    if request.method == 'POST':
        user = member.user
        member.user = None
        member.save()
        user.delete()
        if hx_enabled:
            return HttpResponse(status=209, headers={"HX-Refresh": "true"})
        return HttpResponseRedirect(reverse(MEMBERS_VIEW, args=(member.pk, 0,)))

    return render(request, 'users/modals/delete.html',
                  {'member': member, 'member_user': member.user, "hx_enabled": hx_enabled})
