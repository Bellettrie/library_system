import string
from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from members.forms import EditForm, MembershipPeriodForm
from members.models import Member
from utils.time import get_today, get_now


def get_end_date(year, month_second_half):
    if month_second_half:
        year += 1
    return str(year) + "-06-30"


def student_number_exists(student_number):
    return Member.objects.filter(student_number__iendswith=student_number.lstrip(string.ascii_letters)).first()


@transaction.atomic
@permission_required('members.add_member')
def new(request):
    can_change = request.user.has_perm('members.change_committee')
    edit_dms = request.user.has_perm('members.change_committee')
    if request.method == 'POST':
        member = student_number_exists(request.POST['student_number'])
        form = EditForm(can_change, edit_dms, request.POST, {'member': member})
        if form.is_valid() and request.POST.get('end_date') and (member is None or 'make_anyway' in request.POST):
            if not can_change and 'committees' in form.changed_data:
                raise ValueError("Wrong")
            instance = form.save()
            inst = MembershipPeriodForm(request.POST).save(commit=False)
            inst.member = instance
            inst.save()
            if can_change:
                instance.update_groups()
            return HttpResponseRedirect(reverse('members.view', args=(instance.pk, 0,)))
        else:
            if member is not None:
                return render(request, 'members/member_new.html',
                              {'form': form,  'warning': member,
                               'md_form': MembershipPeriodForm(request.POST)})
            return render(request, 'members/member_new.html', {'form': form, 'error': "No end date specified",
                                                         'md_form': MembershipPeriodForm(request.POST)})
    else:
        form = EditForm(can_change, edit_dms)
    md_form = MembershipPeriodForm(initial={'start_date': get_today(),
                                            'end_date': get_end_date(get_now().year,
                                                                     get_now().month > 6)})
    return render(request, 'members/member_new.html', {'form': form, 'md_form': md_form})
