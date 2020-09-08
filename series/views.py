from django.db.models import Q
from django.http import JsonResponse

# Create your views here.
from django.shortcuts import render

from creators.models import Creator
from series.models import Series


def get_series_by_query(request, search_text):
    series = Series.objects.all()
    for word in search_text.split(" "):
        zz = Series.objects.filter(Q(title__icontains=word) | Q(sub_title__icontains=word) | Q(original_title__icontains=word) | Q(original_subtitle__icontains=word))
        i = len(zz)
        j = 0
        while j < i:
            zz = Series.objects.filter(part_of_series__in=zz) | zz
            j = i
            i = len(zz)
        series = series & zz
    list = []
    for serie in series:
        list.append({'id': serie.pk, 'text': serie.get_canonical_title()})
    return JsonResponse({'results': list}, safe=False)


def view_series(request, pk):
    series = Series.objects.get(pk=pk)
    return render(request, 'series_view.html', {'series': series})

