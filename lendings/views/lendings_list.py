from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView

from lendings.models.lending import Lending


class LendingList(PermissionRequiredMixin, ListView):
    permission_required = 'lendings.add_lending'
    model = Lending
    template_name = 'lendings/list.html'
    paginate_by = 10
    ordering = 'end_date'

    def get_queryset(self):
        result_set = Lending.objects.filter(handed_in=False).order_by('end_date')
        return result_set


