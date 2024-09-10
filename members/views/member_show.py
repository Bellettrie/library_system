from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

from members.models import Member


def show(request, member_id, full):
    if not request.user.has_perm('members.view_member'):
        if not hasattr(request.user, 'member'):
            raise PermissionDenied
        member = request.user.member
        if not (member and member.pk == member_id):
            raise PermissionDenied
    member = get_object_or_404(Member, pk=member_id)
    if member.is_anonimysed:
        return render(request, 'members/detail_anonymous.html', {'member': member})
    if full:
        return render(request, 'members/detail_full.html', {'member': member})
    return render(request, 'members/detail.html', {'member': member})
