import random
import string

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from mail.models import mail_member
from members.models import Member


@transaction.atomic
@permission_required('auth.add_user')
def generate_invite_code(request, member_id):
    letters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters) for i in range(16))
    member = get_object_or_404(Member, pk=member_id)
    if member.user:
        member.invitation_code_valid = False
        member.save()

        return HttpResponseRedirect(reverse('members.views', args=(member.pk,)))
    member.invitation_code = result_str
    member.invitation_code_valid = True
    mail_member('mails/invitation.tpl', {'member': member}, member, True)
    member.save()

    return render(request, 'member_detail.html', {'member': member, 'extra': "Invitation mail sent"})
