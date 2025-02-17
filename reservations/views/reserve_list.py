from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from reservations.models import Reservation


@permission_required('reservations.view_reservation')
def reserve_list(request):
    reservations = Reservation.objects.all()
    return render(request, 'reservations/list.html', {"reservations": reservations})
