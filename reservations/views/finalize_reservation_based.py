from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from lendings.procedures.get_end_date import get_end_date
from lendings.procedures.new_lending import create_lending
from reservations.models import Reservation


@transaction.atomic
@permission_required('lendings.add_lending')
def finalize_reservation_based(request, id):
    reservation = get_object_or_404(Reservation, pk=id)
    member = reservation.member
    item = reservation.item
    if item.is_available_for_lending():
        if request.method == 'POST':
            if not member.can_lend_item(item):
                return redirect('/lend/failed_lending/{}/{}/0'.format(item.id, member.id))
            if not member.is_currently_member():
                return redirect('/lend/failed_lending/{}/{}/1'.format(item.id, member.id))
            if member.has_late_items():
                return redirect('/lend/failed_lending/{}/{}/3'.format(item.id, member.id))
            reservation.delete()
            lending = create_lending(item, member, request.user.member, datetime.now().date())
            return render(request, 'lending_finalized.html',
                          {'member': member, 'item': item, "date": lending.end_date})
        return render(request, 'lending_finalize.html',
                      {'member': member, 'item': item, "date": get_end_date(item, member, datetime.now().date())})
    return redirect('/lend/failed_lending/{}/{}/2'.format(item.id, member.id))
