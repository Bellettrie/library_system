from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect

# Create your views here.
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from book_code_generation.forms import EditForm
from book_code_generation.models import normalize_str
from book_code_generation.location_number_creation import get_authors_numbers, CutterCodeRange, generate_author_number
from creators.models import Creator
from series.models import Series
from works.models import Publication, Location


@permission_required('works.change_work')
def get_book_code(request, publication_id, location_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    location = get_object_or_404(Location, pk=location_id)
    title = request.GET.get('title')
    print(title)
    if title:
        publication.title = title
    code = publication.generate_code_full(location)

    return HttpResponse(code)


@permission_required('works.change_work')
def get_book_code_series(request, series_id, location_id):
    publication = get_object_or_404(Series, pk=series_id)
    location = get_object_or_404(Location, pk=location_id)
    title = request.GET.get('title')
    if title:
        publication.title = title
    code = publication.generate_code_full(location)

    return HttpResponse(code)


@permission_required('works.change_work')
def get_creator_number(request, creator_id, location_id):
    location = get_object_or_404(Location, pk=location_id)

    name = request.GET.get('name')
    min_code = None
    max_code = None
    code = None
    char = None
    try:
        creator = Creator.objects.get(id=creator_id)
        if not name:
            name = normalize_str(creator.name + " " + creator.given_names)

        char, min_code, code, max_code = generate_author_number(normalize_str(name), location, exclude_list=[creator])
    except Creator.DoesNotExist:
        if not name:
            return HttpResponse("NONE")
        char, min_code, code, max_code = generate_author_number(normalize_str(name), location, exclude_list=[])

    return HttpResponse(char + " :: " + str(min_code) + " < <b>" + str(code) + "</b> < " + str(max_code))


@permission_required('works.change_work')
def show_letter_list(request):
    locations = Location.objects.all()
    location = request.GET.get('location')
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    atoz = request.GET.get('atoz')
    print(location)
    numbers = []
    out_of_order = set()
    if location and atoz:
        numbers = get_authors_numbers(location, atoz)
        prev = numbers[0]
        for number in numbers:
            if prev.name > number.name and prev.number < number.number:
                out_of_order.add(number)
            prev = number

    return render(request, 'code_list.html',
                  {'locations': locations, 'location': location, 'letters': letters, 'atoz': atoz, 'entries': numbers,
                   'misses': out_of_order})


def view_cutter_numbers(request):
    return render(request, 'list_cutter_numbers.html',
                  {'cutters': CutterCodeRange.objects.all().order_by('from_affix')})


@transaction.atomic
@permission_required('members.change_member')
def edit(request, cutter_id):
    cutter_code = get_object_or_404(CutterCodeRange, pk=cutter_id)
    if request.method == 'POST':

        form = EditForm(request.POST, instance=cutter_code)
        if form.is_valid():
            instance = form.save()
            print(instance)
            return HttpResponseRedirect(reverse('book_code.code_list'))
    else:
        form = EditForm(instance=cutter_code)
    return render(request, 'member_edit.html', {'form': form, 'member': cutter_code})


@transaction.atomic
@permission_required('members.add_member')
def new(request):
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('book_code.code_list'))
    else:
        form = EditForm()
    return render(request, 'member_edit.html', {'form': form})
