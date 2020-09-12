from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponse

# Create your views here.
from django.shortcuts import get_object_or_404

from creators.models import Creator
from works.models import Publication, Location


@permission_required('works.change_work')
def get_book_code(request, publication_id, location_id):
    print(publication_id)
    print(location_id)
    publication = get_object_or_404(Publication, pk=publication_id)
    location = get_object_or_404(Location, pk=location_id)
    code = publication.generate_code_full(location)

    return HttpResponse(code)

