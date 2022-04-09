from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from members.forms import EditForm
from members.models import Member


@transaction.atomic
@permission_required('members.change_member')
def edit(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    can_change = request.user.has_perm('members.change_committee')
    edit_dms = request.user.has_perm('members.change_committee')
    if request.method == 'POST':
        form = EditForm(can_change, edit_dms, request.POST, instance=member)
        if form.is_valid():
            if not can_change and 'committees' in form.changed_data:
                raise ValueError("Wrong")
            form.save()
            if can_change:
                member.update_groups()
            return HttpResponseRedirect(reverse('members.views', args=(member_id,)))
    else:
        form = EditForm(can_change, edit_dms, instance=member)
    return render(request, 'member_edit.html', {'form': form, 'member': member})