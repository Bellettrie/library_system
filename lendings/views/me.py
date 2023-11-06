from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from lendings.models.lending import Lending


class MyLendingList(LoginRequiredMixin, ListView):
    model = Lending
    template_name = 'lendings/detail.html'
    paginate_by = 10
    ordering = 'end_date'

    def get_queryset(self):

        result_set = Lending.objects.filter(member_id=self.request.user.member.pk).order_by('-end_date')
        return result_set
