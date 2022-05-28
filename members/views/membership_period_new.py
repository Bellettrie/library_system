from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from members.forms import MembershipPeriodForm
from members.models import Member
from members.procedures.delete_double_periods import delete_double_periods
from members.views.member_new import get_end_date
from utils.time import get_today, get_now


@transaction.atomic
@permission_required('members.change_member')
def new_membership_period(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    if request.method == 'POST':

        form = MembershipPeriodForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.member = member
            instance.save()
            delete_double_periods(member)
            return HttpResponseRedirect(reverse('members.view', args=(member.pk,)))
    else:
        form = MembershipPeriodForm(instance=member, initial={'start_date': get_today(),
                                                              'end_date': get_end_date(get_now().year,
                                                                                       get_now().month > 6)})
    return render(request, 'members/', {'form': form, 'member': member})
