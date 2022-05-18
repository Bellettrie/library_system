from django.contrib.auth.decorators import permission_required
from django.shortcuts import render


@permission_required('lendings.add_reservation')
def reserve_list(request):
    return render(request, 'reservation_list.html', {})
