from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from members.models import Member


@transaction.atomic
@permission_required('auth.change_user')
def change_user(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    if request.method == 'POST':
        form = PasswordChangeForm(user=member.user, data=request.POST)
        if form.is_valid():
            instance = form.save()

            instance.member = member
            instance.member.user = instance
            instance.member.save()
            instance.save()
            return HttpResponseRedirect(reverse('members.views', args=(instance.member.pk,)))
    else:
        form = PasswordChangeForm(member.user)
    return render(request, 'user_edit.html', {'form': form, 'member': member, 'user': member.user})