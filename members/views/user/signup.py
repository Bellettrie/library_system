from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from members.models import Member

from django.utils import timezone


@transaction.atomic
def signup(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    invitation_code = request.GET.get('key', '')
    if invitation_code == "":
        if not request.user.has_perm('auth.add_user'):
            raise PermissionDenied
        by_invite = False
    else:
        if member.invitation_code != invitation_code:
            return HttpResponse("Wrong invite code")
        if not member.invitation_code_valid:
            return HttpResponse("Member has no valid invitation")
        if member.invitation_code_end_date is None or member.invitation_code_end_date < timezone.now():
            return HttpResponse("Invitation code is no longer valid")
        by_invite = True
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            instance = form.save()
            old_user = member.user
            member.user = None

            instance.member = member
            member.user = instance
            member.invitation_code_valid = False
            member.update_groups()
            member.save()
            instance.save()
            if old_user is not None:
                old_user.delete()
            if by_invite:
                return HttpResponseRedirect(reverse('login'))
            else:
                return HttpResponseRedirect(reverse('members.view', args=(member_id, 0,)))
    else:
        form = UserCreationForm()
    return render(request, 'users/create.html', {'form': form, 'member': member, 'by_invite': by_invite})
