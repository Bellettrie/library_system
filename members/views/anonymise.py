from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from members.models import Member
from members.procedures.anonymise import anonymise_or_except


@transaction.atomic
@permission_required('members.delete_member')
def anonymise(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html', {'what': "anonymise member with name " + member.name})
    anonymise_or_except(member, datetime.now().date(), dry_run=False)
    return HttpResponseRedirect(reverse('members.view', args=(member.pk, 0,)))
