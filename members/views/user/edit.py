from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render


@transaction.atomic
@login_required()
def change_own_password(request, hx_enabled=False):
    member = request.user.member
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
            return HttpResponseRedirect('/')
    else:
        form = PasswordChangeForm(member.user)
    return render(request, 'users/modals/edit.html',
                  {'form': form, 'member': member, 'member_user': member.user, "hx_enabled": hx_enabled})
