import random
import string

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from mail.models import mail_member
from members.forms import SignupForm
from members.models import Member
from datetime import timedelta
from django.utils import timezone


def clean(student_nr: string) -> string:
    return "".join([ele for ele in student_nr if ele.isdigit()])


@transaction.atomic
def self_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if not form.is_valid():
            return render(request, 'members/self_signup.html',
                          {"form": form, "error": "Incorrect form input, likely empty form."})
        f = form.save(commit=False)

        letters = string.ascii_letters + string.digits
        result_str = ''.join(random.choice(letters) for i in range(16))

        try:
            member = get_object_or_404(Member, email=f.email.strip())
        except Http404:
            return render(request, 'members/self_signup.html',
                          {"form": form, "error": "Incorrect form input, no such email address."})
        if clean(member.student_number) != clean(f.student_number):
            return render(request, 'members/self_signup.html',
                          {"form": form, "error": "Incorrect form input, student number does not match."})
        if member.user and (member.user.is_staff or member.user.is_superuser):
            return render(request, 'members/self_signup.html',
                          {"form": form, "error": "Cannot edit superusers this way"})
        member.invitation_code = result_str
        member.invitation_code_valid = True
        member.invitation_code_end_date = timezone.now() + timedelta(days=14)
        member.save()

        mail_member('mails/invitation.tpl', {'member': member}, member, True)

    form = SignupForm(request.POST)
    return redirect("members.self_signupped")


@transaction.atomic
def self_signupped(request):
    return render(request, 'members/self_signup_done.html')
