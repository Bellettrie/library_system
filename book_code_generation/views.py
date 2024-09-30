from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from book_code_generation.forms import EditForm
from book_code_generation.models import CutterCodeRange
from book_code_generation.helpers import normalize_str
from book_code_generation.procedures.location_number_generation import generate_location_number, get_code_pins
from creators.models import Creator
from works.models import Publication, Location


@permission_required('works.change_work')
def get_book_code(request, publication_id, location_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    location = get_object_or_404(Location, pk=location_id)
    title = request.GET.get('title')
    if title:
        publication.title = title
    code = publication.generate_code_full(location)

    return HttpResponse(code)


def get_book_code_series(series):
    location = series.location
    code = series.generate_code_full(location)

    return code


@permission_required('works.change_work')
def get_creator_number(request, creator_id, location_id):
    location = get_object_or_404(Location, pk=location_id)

    name = request.GET.get('name')
    try:
        creator = Creator.objects.get(id=creator_id)
        if not name:
            name = normalize_str(creator.name + " " + creator.given_names)

        char, min_code, code, max_code = generate_location_number(normalize_str(name), location, exclude_list=[creator])
        return HttpResponse(char + " :: " + str(min_code) + " < <b>" + str(code) + "</b> < " + str(max_code))
    except Creator.DoesNotExist:
        if not name:
            return HttpResponse("NONE")
        char, min_code, code, max_code = generate_location_number(normalize_str(name), location, exclude_list=[])
        return HttpResponse(char + " :: " + str(min_code) + " < <b>" + str(code) + "</b> < " + str(max_code))


@permission_required('works.change_work')
def show_letter_list(request):
    locations = Location.objects.all()
    location = request.GET.get('location')
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    atoz = request.GET.get('atoz')
    numbers = []
    out_of_order = set()
    if location and atoz:
        numbers = get_code_pins(location, atoz)
        prev = numbers[0]
        for number in numbers:
            if prev.name > number.name and int(prev.number) < int(number.number):
                out_of_order.add(number)
            prev = number

    return render(request, 'book_code_generation/code_list.html',
                  {'locations': locations, 'location': location, 'letters': letters, 'atoz': atoz, 'entries': numbers,
                   'misses': out_of_order})


@permission_required('works.change_work')
def view_cutter_numbers(request):
    return render(request, 'book_code_generation/cutter_numbers_list.html',
                  {'cutters': CutterCodeRange.objects.all().order_by('from_affix')})


@transaction.atomic
@permission_required('works.change_work')
def edit(request, cutter_id):
    cutter_code = get_object_or_404(CutterCodeRange, pk=cutter_id)
    if request.method == 'POST':

        form = EditForm(request.POST, instance=cutter_code)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('book_code.code_list'))
    else:
        form = EditForm(instance=cutter_code)
    return render(request, 'book_code_generation/cutter_numbers_edit.html', {'form': form, 'member': cutter_code})


@transaction.atomic
@permission_required('works.change_work')
def new(request):
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('book_code.code_list'))
    else:
        form = EditForm()
    return render(request, 'book_code_generation/cutter_numbers_edit.html', {'form': form})
