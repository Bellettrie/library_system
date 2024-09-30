from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView

from book_code_generation.location_number_creation import generate_author_number
from book_code_generation.views import get_book_code_series
from creators.models import Creator, LocationNumber
from series.forms import SeriesCreateForm, CreatorToSeriesFormSet
from series.models import Series, SeriesNode
from book_code_generation.procedures.validate_cutter_range import validate_cutter_range, InvalidCutterRangeError
from utils.get_query_words import get_query_words
from works.views import word_to_regex


def get_series_by_query(request, search_text):
    series = Series.objects.all()

    for word in search_text.replace("%20", " ").split(" "):
        zz = Series.objects.filter(
            Q(title__icontains=word) | Q(sub_title__icontains=word) | Q(original_title__icontains=word) | Q(
                original_subtitle__icontains=word) | Q(article__icontains=word) | Q(original_article__icontains=word))
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
    series = get_object_or_404(Series, pk=pk)
    return render(request, 'series/view.html', {'series': series})


@transaction.atomic
@permission_required('series.change_series')
def edit_series(request, pk):
    series = None
    creators = None
    if request.method == 'POST':
        if pk is not None:
            series = get_object_or_404(Series, pk=pk)
            form = SeriesCreateForm(request.POST, instance=series)
            creators = CreatorToSeriesFormSet(request.POST, request.FILES, instance=series)
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
                for inst in creators.deleted_objects:
                    inst.delete()
                for c2w in instances:
                    c2w.series = instance
                    c2w.save()

            if series is not None:
                from search.models import SeriesWordMatch
                SeriesWordMatch.series_rename(series)

            return HttpResponseRedirect(reverse('series.views', args=(instance.pk,)))
    else:
        if pk is not None:
            series = get_object_or_404(Series, pk=pk)
            creators = CreatorToSeriesFormSet(instance=series)
            form = SeriesCreateForm(instance=series)
        else:
            creators = CreatorToSeriesFormSet()
            form = SeriesCreateForm()

    return render(request, 'series/edit.html', {'series': series, 'form': form, 'creators': creators})


@permission_required('series.add_series')
def new_series(request):
    return edit_series(request, pk=None)


@permission_required('series.delete_series')
def delete_series(request, pk):
    series = Series.objects.filter(pk=pk)
    z = SeriesNode.objects.filter(part_of_series=series.first())
    if len(z) > 0:
        return render(request, 'are-you-sure.html', {
            'what': "To delete " + (series.first().title or "<No name> ") + ", it has to have no sub-series."})
    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html',
                      {'what': "delete series with name " + (series.first().title or "<No name> ")})
    series.delete()

    return redirect('homepage')


class SeriesList(ListView):
    model = Series
    template_name = 'series/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        return context

    def get_queryset(self):  # new
        words = get_query_words(self.request.GET.get('q', ""))
        if words is None:
            return []
        result = None
        for word in words:
            word = word_to_regex(word)
            if len(word) == 0:
                return []
            authors = Creator.objects.filter(Q(name__iregex=word) | Q(given_names__iregex=word))

            series = set(Series.objects.filter(Q(creatortoseries__creator__in=authors)
                                               | Q(title__iregex=word)
                                               | Q(sub_title__iregex=word)
                                               | Q(original_title__iregex=word)
                                               | Q(original_subtitle__iregex=word)
                                               ))
            if result is None:
                result = series
            else:
                result = series & result
        if result is None:
            return []
        return list(result)


@transaction.atomic
@permission_required('series.change_series')
def new_codegen(request, pk, hx_enabled=False):
    templ = 'series/series_cutter_number/code_gen.html'
    if hx_enabled:
        templ = 'series/series_cutter_number/code_gen_hx.html'
    series = get_object_or_404(Series, pk=pk)

    if request.method == 'POST':
        bk = request.POST.get("book_code")
        if bk is not None:
            series.book_code = bk
            series.save()
            if hx_enabled:
                return HttpResponse(status=209, headers={"HX-Refresh": "true"})
            else:
                return HttpResponseRedirect(reverse('series.views', args=(pk,)))
    return render(request, templ,
                  {"series": series, "recommended_code": get_book_code_series(series)})


@transaction.atomic
@permission_required('series.change_series')
def location_code_set_form(request, pk, hx_enabled=False):
    templ = 'series/series_cutter_number/cutter_gen_form.html'
    if hx_enabled:
        templ = 'series/series_cutter_number/cutter_gen_form_hx.html'
    series = get_object_or_404(Series, pk=pk)
    if series.location_code:
        return render(request, templ, {"series": series, "error": "Already has a location code."})
    if request.method == "POST":
        prefix = request.POST.get("prefix", "{title} ({pk})".format(title=series.title, pk=series.pk)).upper()
        letter = request.POST.get("cutter_letter")
        number = request.POST.get("cutter_number")

        try:
            validate_cutter_range(series.location, prefix, letter, number)
        except InvalidCutterRangeError as e:
            return render(request, templ, {"series": series, "error": e.message, "letter": letter, "number": number})

        series.location_code = LocationNumber.objects.create(location=series.location, number=number, letter=letter,
                                                             name=prefix)

        series.save()
        if hx_enabled:
            return HttpResponse(status=209, headers={"HX-Refresh": "true"})
        return HttpResponseRedirect(reverse('series.gen_code', args=(pk,)))

    return render(request, templ, {"series": series, "letter": "UNKNOWN"})


@permission_required('series.change_series')
def location_code_set_gen(request, pk):
    series = get_object_or_404(Series, pk=pk)
    prefix = request.POST.get("prefix", "{title} ({pk})".format(title=series.title, pk=series.pk)).upper()
    lst = []
    if series.location_code:
        lst = [series.location_code.pk]
    letter, beg, val, end = generate_author_number(prefix, series.location, exclude_location_list=lst)
    return render(request,
                  'book_code_generation/number_result_template.html',
                  {"letter": letter, "number": val, "beg": beg, "end": end})


@transaction.atomic
@permission_required('series.change_series')
def location_code_delete_form(request, pk, hx_enabled=False):
    templ = 'series/series_cutter_number/cutter_delete.html'
    if hx_enabled:
        templ = 'series/series_cutter_number/cutter_delete_hx.html'
    series = get_object_or_404(Series, pk=pk)
    if request.POST:
        lc = series.location_code
        series.location_code = None
        series.save()
        lc.delete()
        if hx_enabled:
            return HttpResponse(status=209, headers={"HX-Refresh": "true"})
        else:
            return HttpResponseRedirect(reverse('series.views', args=(pk,)))
    return render(request, templ,
                  {"series": series})
