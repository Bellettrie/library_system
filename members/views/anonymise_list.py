import datetime

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from members.exceptions import AnonymisationException
from members.models import Member
from members.procedures.anonymise import anonymise_or_except


@transaction.atomic
@permission_required('members.delete_member')
def anonymise_list(request):
    errors = []
    for member_pk in request.POST.getlist('member'):
        member = Member.objects.get(pk=member_pk)
        try:
            anonymise_or_except(member, datetime.date.today(), dry_run=False)
            if member.can_be_deleted() and member.reunion_period_ended():
                member.delete()
        except AnonymisationException as e:
            errors.append("{} {}".format(member, e))
        else:
            errors.append(member)
    if len(errors) > 0:
        return HttpResponse("<br/>".join(errors))
    return HttpResponseRedirect(reverse('members.list.anon'))
