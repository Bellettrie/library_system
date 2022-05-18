from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from lendings.lendingException import LendingImpossibleException
from lendings.procedures.get_end_date import get_end_date
from lendings.procedures.new_lending import create_lending, new_lending
from reservations.models import Reservation


@transaction.atomic
@permission_required('lendings.add_lending')
def finalize_reservation_based(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    member = reservation.member
    item = reservation.item
    if request.method == "POST":
        try:
            lending = new_lending(item, member, request.user.member, datetime.date(datetime.now()), True)
            return render(request, 'lending_finalized.html',
                          {'member': member, 'item': item, "date": lending.end_date})
        except LendingImpossibleException as error:
            return render(request, 'lending_cannot_lend.html',
                          {'member': member, 'item': item, 'error': error})

    return render(request, 'lending_finalize.html',
                  {'member': member, 'item': item, "date": get_end_date(item, member, datetime.now().date())})
