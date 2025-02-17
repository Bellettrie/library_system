from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404

from members.models import Member
from works.views import get_works


@permission_required('lendings.add_lending')
def member_based(request, member_id):
    q = None
    if 'q' in request.GET.keys():
        q = request.GET.get('q')
    items = []
    if q is not None:
        items = get_works(request)
    return render(request, 'lendings/based_on_member.html',
                  {'items': items, 'member': get_object_or_404(Member, pk=member_id)})
