from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from members.models import Member


@transaction.atomic
@permission_required('auth.delete_user')
def delete_user(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    user = member.user
    member.user = None
    member.save()
    user.delete()

    return HttpResponseRedirect(reverse('members.views', args=(member.pk,)))


@transaction.atomic
@permission_required('auth.delete_user')
def delete_user_prompt(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    return render(request, 'users/delete.html', {'member': member, 'user': member.user})
