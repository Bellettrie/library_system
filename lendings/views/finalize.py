
from datetime import datetime, timedelta

from django.contrib.auth.decorators import permission_required, login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from lendings.models.lending import Lending

from members.models import Member

from works.models import Item


@transaction.atomic
@permission_required('lendings.add_lending')
def finalize(request, work_id, member_id):
    member = get_object_or_404(Member, pk=member_id)
    item = get_object_or_404(Item, pk=work_id)
    if item.is_available_for_lending():
        if request.method == 'POST':
            if not member.can_lend_item_type(item.location.category.item_type):
                return redirect('/lend/failed_lending/{}/{}/0'.format(work_id, member_id))
            if not member.is_currently_member():
                return redirect('/lend/failed_lending/{}/{}/1'.format(work_id, member_id))
            if member.has_late_items():
                return redirect('/lend/failed_lending/{}/{}/3'.format(work_id, member_id))
            if item.is_reserved() and not item.is_reserved_for(member):
                return redirect('/lend/failed_lending/{}/{}/4'.format(work_id, member_id))
            lending = Lending.create_lending(item, member, request.user.member)
            return render(request, 'lending_finalized.html',
                          {'member': member, 'item': item, "date": lending.end_date})
        return render(request, 'lending_finalize.html',
                      {'member': member, 'item': item, "date": Lending.calc_end_date(member, item)})
    return redirect('/lend/failed_lending/{}/{}/2'.format(work_id, member_id))