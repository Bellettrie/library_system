from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.urls import reverse
from django.views.generic import ListView

from recode.models import Recode


class RecodeList(PermissionRequiredMixin, ListView):
    permission_required = 'recode.view_recode'
    model = Recode
    template_name = 'recode/list.html'
    paginate_by = 50

    def get_queryset(self):  # new
        loc = self.request.GET.get('location')
        codes = []
        if loc:
            codes = Recode.objects.filter(item__location=loc)
        else:
            codes = Recode.objects.all()
        return codes.order_by('item__book_code')


@transaction.atomic
@permission_required('recode.change_recode')
def recode_finish(request, pk, hx_enabled=False):
    templ = 'recode/recode_finish.html'

    recode = get_object_or_404(Recode, pk=pk)
    if request.method == 'POST':
        item = recode.item
        item.book_code = recode.book_code
        item.book_code_extension = recode.book_code_extension
        item.save()
        recode.delete()

        alt = reverse('recode.list')
        if hx_enabled:
            return HttpResponse(status=209, headers={"HX-Refresh": "true"})
        else:
            return redirect(alt)
    return render(request, templ, {'recode': recode, "hx_enabled": hx_enabled})
