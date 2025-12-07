import re

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.db.models import QuerySet
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView

from book_code_generation.procedures.location_number_generation import generate_location_number
from book_code_generation.views import get_book_code_series
from creators.models import LocationNumber
from search.procedures.search_query.filters import AnyWordFilter
from series.forms import SeriesForm
from series.models import SeriesV2
from book_code_generation.procedures.validate_cutter_range import validate_cutter_range, InvalidCutterRangeError
from utils.get_query_words import get_query_words
from works.forms import WorkForm, CreatorToWorkFormSet
from works.models import CreatorToWork, Work
from search.procedures.search_query.search_query import SearchQuery


def word_to_regex(word: str):
    if re.match('^[\\w-]+?$', word.replace("*", "").replace("+", "").replace("?", "")) is None:
        return ""
    word = word.replace("*", ".*")
    word = word.replace("?", ".?")
    word = word.replace("+", ".+")
    return "(?<!\\S)" + word + "(?!\\S)"


class SeriesOnlyFilter:
    def filter(self, query: QuerySet[Work]) -> QuerySet[Work]:
        return query.filter(seriesv2__isnull=False)


def get_series_by_query(request, search_text):
    words = get_query_words(search_text)

    sq = SearchQuery()
    sq.add_filter(SeriesOnlyFilter())
    sq.add_filter(AnyWordFilter(words))

    result = []
    for row in sq.search().all():
        result.append({'id': row.work_id, 'text': row.work.get_title()})

    return JsonResponse({'results': result}, safe=False)


@transaction.atomic
@permission_required('series.change_series')
def edit_series(request, pk):
    series = None
    creators = None
    if request.method == 'POST':
        if pk is not None:
            series = get_object_or_404(SeriesV2, work_id=pk)
            work_form = WorkForm(request.POST, instance=series.work)

            form = SeriesForm(request.POST, instance=series)
            creators = CreatorToWorkFormSet(request.POST, request.FILES, instance=series.work)
        else:
            form = SeriesForm(request.POST)
            work_form = WorkForm(request.POST)
            creators = CreatorToWorkFormSet(request.POST, request.FILES)
        if form.is_valid():
            if work_form.is_valid():
                work_inst = work_form.save(commit=False)
                work_inst.is_translated = not not work_inst.original_language
                work_inst.save()
            else:
                return render(request, 'series/edit.html',
                              {'series': series, 'form': form, 'work_form': work_form, 'creators': creators})
            instance = form.save(commit=False)
            instance.work_id = work_inst.id
            instance.save()

            if creators.is_valid():
                instances = creators.save(commit=False)
                for inst in creators.deleted_objects:
                    inst.delete()
                for c2w in instances:
                    c2w.work = work_inst
                    c2w.save()

            return HttpResponseRedirect(reverse('work.view', args=(instance.work.pk,)))
    else:
        if pk is not None:
            series = get_object_or_404(SeriesV2, work_id=pk)
            work_form = WorkForm(instance=series.work)
            creators = CreatorToWorkFormSet(instance=series.work)
            form = SeriesForm(instance=series)
        else:
            work_form = WorkForm(request.POST)
            creators = CreatorToWorkFormSet()
            form = SeriesForm()

    return render(request, 'series/edit.html',
                  {'series': series, 'form': form, 'work_form': work_form, 'creators': creators})


@permission_required('series.add_series')
def new_series(request):
    return edit_series(request, pk=None)


@permission_required('series.delete_series')
def delete_series(request, pk):
    wk = Work.objects.filter(id=pk)

    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html',
                      {'what': "delete series with name " + (wk.first().title or "<No name> ")})
    CreatorToWork.objects.filter(work_id=pk).delete()
    wk.delete()

    return redirect('homepage')


class SeriesList(ListView):
    model = Work
    template_name = 'series/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        return context

    def get_queryset(self):  # new
        words = get_query_words(self.request.GET.get('q', None))
        if words is None or len(words) == 0:
            return []
        sq = SearchQuery()
        sq.add_filter(SeriesOnlyFilter())
        sq.add_filter(AnyWordFilter(words))
        return sq.search()


@transaction.atomic
@permission_required('series.change_series')
def new_codegen(request, pk, hx_enabled=False):
    templ = 'series/series_cutter_number/code_gen.html'

    series = get_object_or_404(SeriesV2, work_id=pk)

    if request.method == 'POST':
        bk = request.POST.get("book_code")
        if bk is not None:
            series.book_code = bk
            series.save()
            if hx_enabled:
                return HttpResponse(status=209, headers={"HX-Refresh": "true"})
            else:
                return HttpResponseRedirect(reverse('work.view', args=(pk,)))
    return render(request, templ,
                  {"series": series, "recommended_code": get_book_code_series(series), "hx_enabled": hx_enabled})


@transaction.atomic
@permission_required('series.change_series')
def location_code_set_form(request, pk, hx_enabled=False):
    templ = 'series/series_cutter_number/cutter_gen_form.html'

    series = get_object_or_404(SeriesV2, work_id=pk)
    if series.location_code:
        return render(request, templ,
                      {"series": series, "error": "Already has a location code.", "hx_enabled": hx_enabled})
    if request.method == "POST":
        prefix = request.POST.get("prefix", "{title} ({pk})".format(title=series.work.title, pk=series.pk)).upper()
        letter = request.POST.get("cutter_letter")
        number = request.POST.get("cutter_number")

        try:
            validate_cutter_range(series.location, prefix, letter, number)
        except InvalidCutterRangeError as e:
            return render(request, templ, {"series": series, "error": e.message, "letter": letter, "number": number,
                                           "hx_enabled": hx_enabled})

        series.location_code = LocationNumber.objects.create(location=series.location, number=number, letter=letter,
                                                             name=prefix)

        series.save()
        if hx_enabled:
            return HttpResponse(status=209, headers={"HX-Refresh": "true"})
        return HttpResponseRedirect(reverse('series.gen_code', args=(pk,)))
    return render(request, templ, {"series": series, "letter": "UNKNOWN", "hx_enabled": hx_enabled})


@permission_required('series.change_series')
def location_code_set_gen(request, pk):
    series = get_object_or_404(SeriesV2, work_id=pk)
    prefix = request.POST.get("prefix", "{title} ({pk})".format(title=series.work.title, pk=series.pk)).upper()
    lst = []
    if series.location_code:
        lst = [series.location_code.pk]
    letter, beg, val, end = generate_location_number(prefix, series.location, exclude_location_list=lst)
    return render(request,
                  'book_code_generation/number_result_template.html',
                  {"letter": letter, "number": val, "beg": beg, "end": end})


@transaction.atomic
@permission_required('series.change_series')
def location_code_delete_form(request, pk, hx_enabled=False):
    templ = 'series/series_cutter_number/cutter_delete.html'
    series = get_object_or_404(SeriesV2, work_id=pk)
    if request.POST:
        lc = series.location_code
        series.location_code = None
        series.save()
        lc.delete()
        if hx_enabled:
            return HttpResponse(status=209, headers={"HX-Refresh": "true"})
        else:
            return HttpResponseRedirect(reverse('work.view', args=(pk,)))
    return render(request, templ,
                  {"series": series, 'hx_enabled': hx_enabled})
