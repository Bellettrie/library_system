from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from members.forms import EditForm, MembershipPeriodForm
from utils.time import get_today, get_now


def get_end_date(year, month_second_half):
    if month_second_half:
        year += 1
    return str(year) + "-06-30"


@transaction.atomic
@permission_required('members.add_member')
def new(request):
    can_change = request.user.has_perm('members.change_committee')
    edit_dms = request.user.has_perm('members.change_committee')
    if request.method == 'POST':
        form = EditForm(can_change, edit_dms, request.POST)
        if form.is_valid() and request.POST.get('end_date'):
            if not can_change and 'committees' in form.changed_data:
                raise ValueError("Wrong")
            instance = form.save()
            inst = MembershipPeriodForm(request.POST).save(commit=False)
            inst.member = instance
            inst.save()
            if can_change:
                instance.update_groups()
            return HttpResponseRedirect(reverse('members.view', args=(instance.pk,)))
        else:
            return render(request, 'member_edit.html', {'form': form, 'new': True, 'error': "No end date specified",
                                                        'md_form': MembershipPeriodForm(request.POST)})
    else:
        form = EditForm(can_change, edit_dms)
    md_form = MembershipPeriodForm(initial={'start_date': get_today(),
                                            'end_date': get_end_date(get_now().year,
                                                                     get_now().month > 6)})
    return render(request, 'member_edit.html', {'form': form, 'new': True, 'md_form': md_form})
