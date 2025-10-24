from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.urls import reverse
from django.views.generic import ListView

from recode.forms import RecodeForm
from recode.models import Recode
from works.models import Item


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


@transaction.atomic
@permission_required('works.change_item')
def recode_edit(request, item_id, hx_enabled=False):
    item = get_object_or_404(Item, pk=item_id)
    prev_recodes = Recode.objects.filter(item=item)
    form = RecodeForm()
    if len(prev_recodes) > 0:
        form = RecodeForm()
        form.fields['book_code'].initial = prev_recodes[0].book_code
        form.fields['book_code_extension'].initial = prev_recodes[0].book_code_extension
    else:
        form.fields['book_code'].initial = item.book_code
        form.fields['book_code_extension'].initial = item.book_code_extension
    if request.POST:
        form = RecodeForm(request.POST)
        if form.is_valid():
            book_code = form.cleaned_data['book_code']
            book_code_extension = form.cleaned_data['book_code_extension']
            Recode.objects.filter(item=item).delete()
            if request.POST.get("submit") == "apply_recode" or (item.book_code == book_code and item.book_code_extension == book_code_extension):
                item.book_code = book_code
                item.book_code_extension = book_code_extension
                item.save()
            else:
                Recode.objects.create(item=item, book_code=book_code, book_code_extension=book_code_extension)

            if hx_enabled:
                return HttpResponse(status=209, headers={"HX-Refresh": "true"})
            else:
                return redirect(reverse('recode.list'))
    return render(request, 'recode/edit.html',
                  {'form': form, 'item': item, "hx_enabled": hx_enabled, "had_recode": len(prev_recodes) > 0})
