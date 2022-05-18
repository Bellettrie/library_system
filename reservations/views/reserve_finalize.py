from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from lendings.procedures.get_end_date import get_end_date
from mail.models import mail_member
from members.models import Member
from reservations.models import Reservation
from works.models import Item


@transaction.atomic
def reserve_finalize(request, work_id, member_id):
    if not request.user.has_perm('lendings.add_reservation'):
        if not hasattr(request.user, 'member'):
            raise PermissionDenied
        member = request.user.member
        if not (member and member.id == member_id):
            raise PermissionDenied
    member = get_object_or_404(Member, pk=member_id)
    item = get_object_or_404(Item, pk=work_id)
    if request.method == 'POST':
        if not member.can_lend_more_of_item(item):
            return redirect('/lend/failed_reservation/{}/{}/0'.format(work_id, member_id))
        if not member.is_currently_member():
            return redirect('/lend/failed_reservation/{}/{}/1'.format(work_id, member_id))
        if member.has_late_items():
            return redirect('/lend/failed_reservation/{}/{}/3'.format(work_id, member_id))
        if item.is_reserved():
            return redirect('/lend/failed_reservation/{}/{}/4'.format(work_id, member_id))
        Reservation.create_reservation(item, member, request.user.member)
        return render(request, 'reserve_finalized.html',
                      {'member': member, 'item': item})

        if item.is_lent_out():
            mail_member('mails/book_just_got_reserved.tpl',
                        {'member': item.current_lending().member, 'item': item}, item.current_lending().member, True)

    return render(request, 'reserve_finalize.html',
                  {'member': member, 'item': item, "date": get_end_date(item, member, datetime.now().date())})
