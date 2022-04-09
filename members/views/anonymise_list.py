from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from members.models import Member


@transaction.atomic
@permission_required('members.delete_member')
def anonymise_list(request):
    # return HttpResponse("HI")
    errors = []
    for member_pk in request.POST.getlist('member'):
        member = Member.objects.get(pk=member_pk)
        if member.should_be_anonymised():
            member.anonymise_me(dry_run=False)
            if member.can_be_deleted():
                member.delete()
        else:
            errors.append(member)
    if len(errors) > 0:
        return HttpResponse(" ".join(errors))
    return HttpResponseRedirect(reverse('members.list.anon'))