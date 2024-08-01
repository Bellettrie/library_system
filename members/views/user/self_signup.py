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

from members.views.user.invite_code_generate import handle_member_invite


def clean(student_nr: string) -> string:
    return "".join([ele for ele in student_nr if ele.isdigit()])


@transaction.atomic
def self_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if not form.is_valid():
            return render(request, 'members/self_signup.html',
                          {"form": form, "error": "Incorrect form input, likely empty form."})

        # Retrieve incomplete member object as supplied by form
        member_form_data = form.save(commit=False)

        # Retrieve member data
        try:
            member = get_object_or_404(Member, primary_email=member_form_data.primary_email.strip())
        except Http404:
            return render(request, 'members/self_signup.html',
                          {"form": form, "error": "Incorrect form input, no such email address."})

        # Verify that the member data is consistent
        if clean(member.student_number) != clean(member_form_data.student_number):
            return render(request, 'members/self_signup.html',
                          {"form": form, "error": "Incorrect form input, student number does not match."})
        if member.user and (member.user.is_staff or member.user.is_superuser):
            return render(request, 'members/self_signup.html',
                          {"form": form, "error": """Due to the permissions you have, resetting your account this
                                                   way would be a security risk. Please contact the web committee for
                                                   help."""})

        handle_member_invite(member)

        return redirect("members.self_signupped")
    else:
        # New empty form
        form = SignupForm(request.POST)
        return render(request, 'members/self_signup.html', {"form": form})


@transaction.atomic
def self_signupped(request):
    return render(request, 'members/self_signup_done.html')
