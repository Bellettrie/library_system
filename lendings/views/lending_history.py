from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from lendings.models.lending import Lending
from works.models import Item


class LendingHistory(PermissionRequiredMixin, ListView):
    permission_required = 'lendings.add_lending'
    model = Lending
    template_name = 'lendings/history.html'
    paginate_by = 20
    ordering = 'end_date'

    def get_queryset(self, *args, **kwargs):
        result_set = Lending.objects.filter(item_id=self.kwargs['item_id']).order_by('-end_date')
        return result_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        advanced = self.request.GET.get("advanced", False)
        context['advanced'] = advanced

        context['item'] = get_object_or_404(Item, pk=self.kwargs['work_id'])
        return context
