from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic import ListView

from recode.models import Recode


class RecodeList(PermissionRequiredMixin, ListView):
    permission_required = 'recode.view_recode'
    model = Recode
    template_name = 'recodings_list.html'
    paginate_by = 50
    def get_queryset(self):  # new
        loc = self.request.GET.get('location')
        if loc:
            return Recode.objects.filter(item__location=loc)
        else:
            return Recode.objects.all()


@transaction.atomic
@permission_required('recode.change_recode')
def end_recode(request, pk):
    recode = Recode.objects.get(pk=pk)
    item = recode.item
    item.book_code = recode.book_code
    item.book_code_extension = recode.book_code_extension
    item.save()
    recode.delete()

    alt = reverse('recode.list')
    a = request.GET.get('next')
    if a:
        return redirect(a)
    else:
        return redirect(alt)
