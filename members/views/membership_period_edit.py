from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from members.forms import MembershipPeriodForm
from members.models import MembershipPeriod
from members.procedures.delete_double_periods import delete_double_periods


@transaction.atomic
@permission_required('members.change_member')
def edit_membership_period(request, membership_period_id):
    membership_period = get_object_or_404(MembershipPeriod, pk=membership_period_id)
    if request.method == 'POST':
        form = MembershipPeriodForm(request.POST, instance=membership_period)
        if form.is_valid():
            form.save()
            delete_double_periods(membership_period.member)
            return HttpResponseRedirect(reverse('members.view', args=(membership_period.member.pk, 0,)))
    else:
        form = MembershipPeriodForm(instance=membership_period)

    return render(request, 'members/membership_edit.html', {'form': form, 'member': membership_period})
