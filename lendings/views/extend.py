from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from lendings.lendingException import LendingImpossibleException
from lendings.models.lending import Lending
from lendings.procedures.extend import extend_lending, new_extension
from lendings.procedures.get_end_date import get_end_date

from works.models import Item


@transaction.atomic
def extend(request, work_id):
    item = get_object_or_404(Item, pk=work_id)
    lending = item.current_lending()

    # Permission checks
    if not request.user.has_perm('lendings.extend'):
        if not hasattr(request.user, 'member'):
            # The user who tries to extend is not linked to a member
            return render(request, 'lending_cannot_extend.html',
                          {'member': lending.member, 'item': lending.item, 'error': "Please contact the web committee, something is spectacularly wrong"})
        member = request.user.member
        if not (member and member == request.user.member):
            # A user without the extend any permission tries to extend someone elses book
            return render(request, 'lending_cannot_extend.html',
                          {'member': lending.member, 'item': lending.item, 'error': "You lack the permissions to extend an item that you did borrow for yourself."})
    late_days = datetime.now().date() - lending.end_date

    # Post checks
    if request.method == 'POST':
        try:
            new_extension(lending, datetime.now().date())
            return render(request, 'lending_extended.html',
                          {'member': lending.member,
                           'item': item,
                           "date": lending.end_date
                           })
        except LendingImpossibleException as error:
            return render(request, 'lending_cannot_extend.html',
                          {'member': lending.member, 'item': lending.item, 'error': error})
    else:
        return render(request, 'lending_extend.html',
                      {'member': lending.member,
                       'item': item,
                       'end_date': lending.end_date,
                       'is_changed': lending.end_date < get_end_date(item, lending.member, datetime.now().date()),
                       "date": get_end_date(item, lending.member, datetime.now().date()),
                       'late': lending.end_date < datetime.now().date(),
                       'days_late': late_days.days,
                       'fine': lending.calculate_fine()
                       })