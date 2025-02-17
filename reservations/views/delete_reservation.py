from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
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
    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html', {'hx_enabled':hx_enabled, 'what': "Delete reservation for book " + reservation.item.publication.get_title()})

    reservation.delete()

    return render(request, 'reservations/delete.html')
