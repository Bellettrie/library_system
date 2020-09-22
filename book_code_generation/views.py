from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponse

# Create your views here.
from django.shortcuts import get_object_or_404, render

from book_code_generation.models import generate_author_number, get_authors_numbers, turbo_str
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
    creator = Creator.objects.get(id=creator_id)

    code = generate_author_number(turbo_str(creator.name + " " + creator.given_names), location, exclude_list=[creator])

    return HttpResponse(code)


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

    return render(request, 'code_list.html', {'locations': locations, 'location': location, 'letters': letters, 'atoz': atoz, 'entries': numbers, 'misses': out_of_order})
