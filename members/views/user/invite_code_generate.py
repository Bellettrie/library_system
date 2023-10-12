import random
import string

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from mail.models import mail_member
from members.models import Member
from datetime import timedelta
from django.utils import timezone


def handle_member_invite(member):
    valid_characters = string.ascii_letters + string.digits
    invitation_code = ''.join(random.choice(valid_characters) for _ in range(24))
    member.invitation_code = invitation_code
    member.invitation_code_valid = True
    member.invitation_code_end_date = timezone.now() + timedelta(days=14)
    member.save()
    mail_member('mails/invitation.tpl', {'member': member}, member)


@transaction.atomic
@permission_required('auth.add_user')
def generate_invite_code(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    if member.user:
        member.invitation_code_valid = False
        member.save()

        return HttpResponseRedirect(reverse('members.view', args=(member.pk, 0,)))

    # set invite code
    handle_member_invite(member)

    return render(request, 'members/detail.html', {'member': member, 'extra': "Invitation mail sent"})
