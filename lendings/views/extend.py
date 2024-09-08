from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from lendings.lendingException import LendingImpossibleException
from lendings.models.lending import Lending
from lendings.procedures.extend import extend_lending, new_extension
from lendings.procedures.get_end_date import get_end_date
from utils.time import get_today

from works.models import Item


def hx_extend(request, work_id):
    return extend(request, work_id, hx_enabled=True)
@transaction.atomic
def extend(request, work_id, hx_enabled=False):
    cannot_extend_template='lendings/cannot_extend.html'
    extend_finished_template='lendings/extend_finished.html'
    extend_template='lendings/extend.html'
    if hx_enabled:
        cannot_extend_template = 'lendings/cannot_extend_hx.html'
        extend_finished_template = 'lendings/extend_finished_hx.html'
        extend_template = 'lendings/extend_hx.html'

    item = get_object_or_404(Item, pk=work_id)
    lending = item.current_lending()

    # Permission checks
    if not request.user.has_perm('lendings.extend'):
        if not hasattr(request.user, 'member'):
            # The user who tries to extend is not linked to a member
            return render(request, cannot_extend_template,
                          {'member': lending.member, 'item': lending.item,
                           'error': "Please contact the web committee, something is spectacularly wrong"})
        member = request.user.member
        if not (member and member == request.user.member):
            # A user without the extend any permission tries to extend someone elses book
            return render(request, cannot_extend_template,
                          {'member': lending.member, 'item': lending.item,
                           'error': "You lack the permissions to extend an item that you did borrow for yourself."})
    late_days = get_today() - lending.end_date

    # Post checks
    if request.method == 'POST':
        try:
            new_extension(lending, get_today())
            return render(request, extend_finished_template,
                          {'member': lending.member,
                           'item': item,
                           "date": lending.end_date
                           })
        except LendingImpossibleException as error:
            return render(request, cannot_extend_template,
                          {'member': lending.member, 'item': lending.item, 'error': error})
    else:
        return render(request, extend_template,
                      {'member': lending.member,
                       'item': item,
                       'end_date': lending.end_date,
                       'is_changed': lending.end_date < get_end_date(item, lending.member, get_today()),
                       "date": get_end_date(item, lending.member, get_today()),
                       'late': lending.end_date < get_today(),
                       'days_late': late_days.days,
                       'fine': lending.calculate_fine()
                       })
