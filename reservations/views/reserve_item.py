from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404

from works.models import Item


@permission_required('reservations.add_reservation')
def reserve_item(request, item_id):
    from members.views.member_list import query_members
    from utils.get_query_words import get_query_words
    words = get_query_words(request.GET.get("q"))
    members = query_members(words)
    return render(request, 'reservations/based_on_work.html',
                  {'members': members, 'item': get_object_or_404(Item, pk=item_id)})
