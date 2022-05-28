from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404

from lendings.lendingException import LendingImpossibleException
from lendings.procedures.get_end_date import get_end_date
from lendings.procedures.new_lending import new_lending

from members.models import Member
from utils.time import get_today

from works.models import Item


@transaction.atomic
@permission_required('lendings.add_lending')
def finalize(request, work_id, member_id):
    member = get_object_or_404(Member, pk=member_id)
    item = get_object_or_404(Item, pk=work_id)
    if request.method == 'POST':
        try:
            lending = new_lending(item, member, request.user.member, get_today())
            return render(request, 'lendings/finalized.html',
                          {'member': member, 'item': item, "date": lending.end_date})
        except LendingImpossibleException as error:
            return render(request, 'lendings/cannot_lend.html',
                          {'member': member, 'item': item, 'error': error})
    return render(request, 'lendings/finalize.html',
                  {'member': member, 'item': item, "date": get_end_date(item, member, get_today())})
