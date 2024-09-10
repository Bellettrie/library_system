from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from members.models import Member

def change_user_hx(request, member_id):
    return change_user(request, member_id, True)

@transaction.atomic
@permission_required('auth.change_user')
def change_user(request, member_id,hx_enabled=False):
    templ = 'users/edit.html'
    if hx_enabled:
        templ='users/edit_hx.html'
    member = get_object_or_404(Member, pk=member_id)
    if request.method == 'POST':
        form = PasswordChangeForm(user=member.user, data=request.POST)
        if form.is_valid():
            instance = form.save()

            instance.member = member
            instance.member.user = instance
            instance.member.save()
            instance.save()
            if hx_enabled:
                return HttpResponse(status=209, headers={"HX-Redirect": "/"})
            return HttpResponseRedirect(reverse('members.view', args=(instance.member.pk, 0,)))
    else:
        form = PasswordChangeForm(member.user)
    return render(request, templ, {'form': form, 'member': member, 'member_user': member.user})
