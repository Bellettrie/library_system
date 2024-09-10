from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from members.forms import MembershipPeriodForm
from members.models import MembershipPeriod
from members.procedures.delete_double_periods import delete_double_periods


def edit_membership_period_hx(request, membership_period_id):
    return edit_membership_period(request, membership_period_id, True)


@transaction.atomic
@permission_required('members.change_member')
def edit_membership_period(request, membership_period_id, hx_enabled=False):
    templ = 'members/membership_edit.html'
    if hx_enabled:
        templ = 'members/membership_edit_hx.html'
    membership_period = get_object_or_404(MembershipPeriod, pk=membership_period_id)
    if request.method == 'POST':
        form = MembershipPeriodForm(request.POST, instance=membership_period)
        if form.is_valid():
            form.save()
            delete_double_periods(membership_period.member)
            if hx_enabled:
                return HttpResponse(status=209, headers={"HX-Refresh": "true"})
            return HttpResponseRedirect(reverse('members.view', args=(membership_period.member.pk, 0,)))
    else:
        form = MembershipPeriodForm(instance=membership_period)

    return render(request, templ, {'form': form, 'member': membership_period})
