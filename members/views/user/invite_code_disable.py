from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from members.models import Member


@transaction.atomic
@permission_required('auth.delete_user')
def disable_invite_code(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    member.invitation_code_valid = False
    member.save()
    return HttpResponseRedirect(reverse('members.view', args=(member.pk, 0,)))
