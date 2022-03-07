from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from lendings.views.lending_failed import lending_failed_reasons
from members.models import Member
from works.models import Item


@login_required()
def reserve_failed(request, member_id, work_id, reason_id):
    item = get_object_or_404(Item, pk=work_id)
    member = get_object_or_404(Member, pk=member_id)
    organising_member = request.user.member
    return render(request, 'reservation_cannot_reserve.html', {'item': item,
                                                               'member': member, 'organising_member': organising_member,
                                                               'reason': lending_failed_reasons[reason_id]})
