from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from members.forms import EditForm, PrivacyForm
from members.models import Member


@transaction.atomic
@permission_required('members.change_member')
def edit(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    can_change = request.user.has_perm('members.change_committee')
    edit_dms = request.user.has_perm('members.change_committee')
    if request.method == 'POST':
        form = EditForm(can_change, edit_dms, request.POST, instance=member)
        p_form = PrivacyForm(request.POST, instance=member)
        if form.is_valid() and p_form.is_valid():
            form.save()
            p_form.save()
            return HttpResponseRedirect(reverse('members.view', args=(member_id, 0,)))
    else:
        form = EditForm(can_change, edit_dms, instance=member)
        p_form = PrivacyForm(instance=member)
    return render(request, 'members/edit.html', {'form': form, 'member': member, 'privacy_form': p_form})
