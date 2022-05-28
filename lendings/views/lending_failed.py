from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from members.models import Member

from works.models import Item

lending_failed_reasons = {
    0: "Member has too many books",
    1: "Member is not presently a member",
    2: "Item is lent out",
    3: "Member has late items",
    4: "Item is reserved"
}


@login_required()
def lending_failed(request, member_id, work_id, reason_id):
    item = get_object_or_404(Item, pk=work_id)
    member = get_object_or_404(Member, pk=member_id)
    organising_member = request.user.member
    return render(request, 'lendings/cannot_lend.html', {'item': item,
                                                         'member': member, 'organising_member': organising_member,
                                                         'reason': lending_failed_reasons[reason_id]})
