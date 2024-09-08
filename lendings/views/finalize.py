from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404

from config.models import LendingSettings
from lendings.lendingException import LendingImpossibleException
from lendings.procedures.get_end_date import get_end_date
from lendings.procedures.new_lending import new_lending

from members.models import Member
from utils.time import get_today

from works.models import Item


def finalize_hx(request, work_id, member_id):
    return finalize(request, work_id, member_id,hx_enabled=True)


@transaction.atomic
@permission_required('lendings.add_lending')
def finalize(request, work_id, member_id, hx_enabled=False):
    cannot_lend_template='lendings/cannot_lend.html'
    finalize_template = 'lendings/finalize.html'
    finalized_template='lendings/finalized.html'
    if hx_enabled:
        cannot_lend_template='lendings/cannot_lend_hx.html'
        finalize_template='lendings/finalize_hx.html'
        finalized_template='lendings/finalized_hx.html'

    member = get_object_or_404(Member, pk=member_id)
    item = get_object_or_404(Item, pk=work_id)
    lendingsettings = LendingSettings.get_for_type(item.location.category.item_type, member.is_active())
    fee = ""
    if lendingsettings.borrow_money != 0:
        fee = format(lendingsettings.borrow_money / 100, '.2f')
    if request.method == 'POST':
        try:
            lending = new_lending(item, member, request.user.member, get_today())
            return render(request, finalized_template,
                          {'member': member, 'item': item, "date": lending.end_date, 'fee': fee})
        except LendingImpossibleException as error:
            return render(request, cannot_lend_template,
                          {'member': member, 'item': item, 'error': error, 'fee': fee})
    return render(request, finalize_template,
                  {'member': member, 'item': item, "date": get_end_date(item, member, get_today()), 'fee': fee})
