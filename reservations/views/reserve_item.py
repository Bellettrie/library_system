from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404

from reservations.path_names import RESERVE_FINALIZE
from works.models import Item


@permission_required('lendings.add_reservation')
def reserve_item(request, work_id):
    from members.views import query_members
    from utils.get_query_words import get_query_words
    words = get_query_words(request.GET.get("q"))
    members = query_members(words)
    return render(request, 'reserve_based_on_work.html',
                  {'members': members, 'item': get_object_or_404(Item, pk=work_id),
                   "RESERVE_FINALIZE": RESERVE_FINALIZE})
