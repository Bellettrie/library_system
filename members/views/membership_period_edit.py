from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from members.forms import MembershipPeriodForm
from members.models import MembershipPeriod


@transaction.atomic
@permission_required('members.change_member')
def edit_membership_period(request, membership_period_id):
    member = get_object_or_404(MembershipPeriod, pk=membership_period_id)
    if request.method == 'POST':

        form = MembershipPeriodForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            member.member.try_and_delete_double_periods()
            return HttpResponseRedirect(reverse('members.views', args=(member.member.pk,)))
    else:
        form = MembershipPeriodForm(instance=member)

    return render(request, 'member_membership_edit.html', {'form': form, 'member': member})