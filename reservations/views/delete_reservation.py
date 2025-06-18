from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from reservations.models import Reservation


@login_required
def delete_reservation(request, reservation_id, hx_enabled=False):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    if not request.user.has_perm('reservations.delete_reservation'):
        if not hasattr(request.user, 'member'):
            raise PermissionDenied
        member = request.user.member
        if not (member and member.id == reservation.member_id):
            raise PermissionDenied

    if request.method == 'POST':
        reservation.delete()

        if hx_enabled:
            return HttpResponse(status=209, headers={"HX-Refresh": "true"})
        return render(request, 'reservations/delete.html')

    return render(request, 'reservations/modals/cancel.html', {'hx_enabled': hx_enabled, "reservation": reservation})
