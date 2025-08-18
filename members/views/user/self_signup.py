import string

from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from members.forms import SignupForm
from members.models import Member

from members.views.user.invite_code_generate import handle_member_invite


def clean(student_nr: string) -> string:
    return "".join([ele for ele in student_nr if ele.isdigit()])


@transaction.atomic
def self_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if not form.is_valid():
            return render(request, 'members/self_signup.html', {"form": form})

        # Retrieve incomplete member object as supplied by form
        member_form_data = form.save(commit=False)

        # Retrieve member data
        try:
            member = get_object_or_404(Member, primary_email=member_form_data.primary_email.strip())
        except Http404:
            form.add_error(None, "Email address and/or student number is incorrect.")
            return render(request, 'members/self_signup.html', {"form": form})

        # Verify that the member data is consistent
        if clean(member.student_number) != clean(member_form_data.student_number):
            form.add_error(None, "Email address and/or student number is incorrect.")
            return render(request, 'members/self_signup.html', {"form": form})
        if member.user and (member.user.is_staff or member.user.is_superuser):
            form.add_error(None, """Due to the permissions you have, resetting your account this way would be
                                                a security risk. Please contact the web committee for help.""")
            return render(request, 'members/self_signup.html', {"form": form})

        handle_member_invite(member)

        return render(request, 'members/self_signup_done.html')
    else:
        # New empty form
        form = SignupForm()
        return render(request, 'members/self_signup.html', {"form": form})
