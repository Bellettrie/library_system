import string
from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from members.forms import EditForm
from members.models import Member


def student_number_exists(student_number):
    return Member.objects.filter(student_number__iendswith=student_number.lstrip(string.ascii_letters)).first()


@transaction.atomic
@permission_required('members.add_member')
def new(request):
    can_change = False
    edit_dms = False
    if request.method == 'POST':
        member = None
        form = EditForm(can_change, edit_dms, request.POST, {'member': member})
        if form.is_valid() and (member is None or 'make_anyway' in request.POST):
            if 'committees' in form.changed_data:
                raise ValueError("Wrong")
            instance = form.save()
            instance.is_anonimysed = True
            instance.save()
            return HttpResponseRedirect(reverse('members.view', args=(instance.pk, 0,)))
    else:
        form = EditForm(can_change, edit_dms)
    return render(request, 'members/edit.html', {'form': form})