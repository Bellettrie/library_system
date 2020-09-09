from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from creators.models import Creator
from series.forms import SeriesCreateForm, CreatorToSeriesFormSet
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


def edit_series(request, pk):
    series = None
    creators = None
    if request.method == 'POST':
        if pk is not None:
            series = get_object_or_404(Series, pk=pk)
            form = SeriesCreateForm(request.POST, instance=series)
            creators = CreatorToSeriesFormSet(request.POST, request.FILES)
        else:
            form = SeriesCreateForm(request.POST)
            creators = CreatorToSeriesFormSet(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            found_set = set()
            if instance.pk:
                found_set.add(instance)
            # Check for loops!
            walker = instance.part_of_series
            while walker is not None:
                if walker in found_set:
                    raise ValueError("Loop!")
                found_set.add(walker)
                walker = walker.part_of_series
            instance.is_translated = instance.original_language is not None
            instance.save()

            if creators.is_valid():
                instances = creators.save(commit=False)
                for c2w in instances:
                    c2w.series = instance
                    c2w.save()

            return HttpResponseRedirect(reverse('series.view', args=(instance.pk,)))
    else:
        if pk is not None:
            series = get_object_or_404(Series, pk=pk)
            creators = CreatorToSeriesFormSet(instance=series)
            form = SeriesCreateForm(instance=series)
        else:
            creators = CreatorToSeriesFormSet()
            form = SeriesCreateForm()

    return render(request, 'series_edit.html', {'series': series, 'form': form, 'creators': creators})


def new_series(request):
    return edit_series(request, pk=None)
