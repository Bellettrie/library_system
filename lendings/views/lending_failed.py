
from datetime import datetime, timedelta

from django.contrib.auth.decorators import permission_required, login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from lendings.models.lending import Lending
from members.models import Member

from works.models import Item
from works.views import get_works


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
    return render(request, 'lending_cannot_lend.html', {'item': item,
                                                        'member': member, 'organising_member': organising_member,
                                                        'reason': lending_failed_reasons[reason_id]})
