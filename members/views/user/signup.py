from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from members.models import Member


@transaction.atomic
def signup(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    if not request.user.has_perm('auth.add_user'):
        members = Member.objects.filter(pk=member_id, invitation_code=request.GET.get('key', ''))

        if len(members) != 1:
            raise PermissionDenied
        if not members[0].invitation_code_valid:
            raise PermissionDenied
        else:
            print(members[0].invitation_code)
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            instance = form.save()

            instance.member = member
            instance.member.user = instance
            instance.member.invitation_code_valid = False
            instance.member.update_groups()
            instance.member.save()
            instance.save()
            return HttpResponseRedirect(reverse('login'))
    else:
        form = UserCreationForm()
    return render(request, 'user_create.html', {'form': form, 'member': member})