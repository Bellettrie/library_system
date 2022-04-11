from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from reservations.models import Reservation


@permission_required('lendings.add_reservation')
def reserve_list(request):
    reservations = Reservation.objects.order_by('reserved_on')
    return render(request, 'reservation_list.html', {'reservations': reservations})
