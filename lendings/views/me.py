from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.views.generic import ListView

from lendings.models.lending import Lending
from reservations.models import Reservation


class MyLendingList(LoginRequiredMixin, ListView):
    model = Lending
    template_name = 'lendings/detail.html'
    paginate_by = 10
    ordering = 'end_date'

    def get_queryset(self):
        result_set = Lending.objects.filter(member_id=self.request.user.member.pk).order_by('-end_date')
        return result_set


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
