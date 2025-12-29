from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render

from lendings.models.lending import Lending
from reservations.models import Reservation


@login_required()
def lendings_and_reservations(request):
    lendings = Lending.objects.filter(member_id=request.user.member.pk).order_by('-end_date')
    paginator = Paginator(lendings, 10)
    page = request.GET.get('page')
    try:
        lendings = paginator.page(page)
    except PageNotAnInteger:
        lendings = paginator.page(1)
    except EmptyPage:
        lendings = paginator.page(paginator.num_pages)

    reservations = Reservation.objects.filter(member_id=request.user.member.pk).order_by('-reserved_on')

    context = {'lendings': lendings, 'reservations': reservations}
    return render(request, 'lendings/detail.html', context)
