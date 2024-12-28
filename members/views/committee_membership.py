from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from members.models import Member, Committee


@transaction.atomic
@permission_required('members.committee_update')
def join_committee(request, member_id, hx_enabled=True):
    member = get_object_or_404(Member, pk=member_id)

    if request.method == 'POST':
        committee_id = request.POST.get('committee_id')
        if committee_id is not None:
            committee = get_object_or_404(Committee, pk=committee_id)
            member.committees.add(committee)
            member.save()

            if hx_enabled:
                return HttpResponse(status=209, headers={"HX-Redirect": "true"})
            return HttpResponseRedirect(reverse('members.view', args=(member_id, 0,)))

    committees = Committee.objects.all()
    templ = 'members/committee/join.html'
    if hx_enabled:
        templ = 'members/committee/join_hx.html'
    return render(request, templ, {'member': member, 'committees': committees})


@transaction.atomic
@permission_required('members.committee_update')
def leave_committee(request, member_id, committee_id, hx_enabled=True):
    member = get_object_or_404(Member, pk=member_id)

    if request.method == 'POST':
        committee = get_object_or_404(Committee, pk=committee_id)
        member.committees.remove(committee)
        member.save()

        if hx_enabled:
            return HttpResponse(status=209, headers={"HX-Redirect": "true"})
        return HttpResponseRedirect(reverse('members.view', args=(member_id, 0,)))

    committees = Committee.objects.all()
    templ = 'members/committee/leave.html'
    if hx_enabled:
        templ = 'members/committee/leave_hx.html'
    return render(request, templ, {'member': member, 'committees': committees})
