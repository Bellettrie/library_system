from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic import ListView

from recode.models import Recode


class RecodeList(ListView):
    model = Recode
    template_name = 'recodings_list.html'
    paginate_by = 50

def end_recode(request, pk):
    print(pk)
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

