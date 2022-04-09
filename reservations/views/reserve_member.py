from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404

from members.models import Member
from reservations.path_names import RESERVE_FINALIZE
from works.views import get_works


@permission_required('lendings.add_reservation')
def reserve_member(request, member_id):
    q = None
    if 'q' in request.GET.keys():
        q = request.GET.get('q')
    items = []
    if q is not None:
        items = get_works(request)
        for row in items:
            row.set_item_options(["finalizeRes"])

    return render(request, 'reserve_based_on_member.html',
                  {'items': items, 'member': get_object_or_404(Member, pk=member_id),
                   "RESERVE_FINALIZE": RESERVE_FINALIZE})
