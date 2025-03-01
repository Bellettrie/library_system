from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, render

from lendings.procedures.get_end_date import get_end_date
from mail.models import mail_member
from members.models import Member
from reservations.procedures.new_reservation import new_reservation
from reservations.reservationException import ReservationImpossibleException
from works.models import Item
from utils.time import get_today


@transaction.atomic
def reserve_finalize(request, work_id, member_id):
    if not request.user.has_perm('reservations.add_reservation'):
        if not hasattr(request.user, 'member'):
            raise PermissionDenied
        member = request.user.member
        if not (member and member.id == member_id):
            raise PermissionDenied
    member = get_object_or_404(Member, pk=member_id)
    item = get_object_or_404(Item, pk=work_id)
    if request.method == 'POST':
        try:
            new_reservation(item, member, request.user.member, get_today())
            if item.is_lent_out():
                mail_member('mails/book_just_got_reserved.tpl',
                            {'member': item.current_lending().member, 'item': item},
                            item.current_lending().member,
                            True)

            return render(request, 'reservations/finalized.html',
                          {'member': member, 'item': item})
        except ReservationImpossibleException as error:
            return render(request, 'reservations/cannot_reserve.html',
                          {'member': member, 'item': item, 'error': error})

    return render(request, 'reservations/finalize.html',
                  {'member': member, 'item': item, "date": get_end_date(item, member, get_today())})
