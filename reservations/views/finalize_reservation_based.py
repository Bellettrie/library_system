from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from lendings.lendingException import LendingImpossibleException
from lendings.procedures.get_end_date import get_end_date
from lendings.procedures.new_lending import create_lending, new_lending
from reservations.models import Reservation
from utils.time import get_today


@transaction.atomic
@permission_required('lendings.add_lending')
def finalize_reservation_based(request, reservation_id, hx_enabled=False):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    member = reservation.member
    item = reservation.item
    if request.method == "POST":
        try:
            lending = new_lending(item, member, request.user.member, get_today(), True)
            return render(request, 'lendings/modals/finalized.html',
                          {'hx_enabled':hx_enabled, 'member': member, 'item': item, "date": lending.end_date})
        except LendingImpossibleException as error:
            return render(request, 'lendings/modals/cannot_lend.html',
                          {'hx_enabled':hx_enabled, 'member': member, 'item': item, 'error': error})

    return render(request, 'lendings/modals/finalize.html',
                  {'hx_enabled':hx_enabled, 'member': member, 'item': item, "date": get_end_date(item, member, get_today())})
