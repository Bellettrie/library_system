
from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from lendings.models.lending import Lending
from lendings.procedures.extend import extend_lending
from lendings.procedures.get_end_date import get_end_date

from works.models import Item


@transaction.atomic
def extend(request, work_id):
    item = get_object_or_404(Item, pk=work_id)
    lending = item.current_lending()
    if not request.user.has_perm('lendings.extend'):
        if not hasattr(request.user, 'member'):
            raise PermissionDenied
        member = request.user.member
        if not (member and member == request.user.member):
            raise PermissionDenied
    late_days = datetime.now().date() - lending.end_date
    if lending.is_extendable(request.user.has_perm('lendings.extend_with_fine')):
        if request.method == 'POST':
            extend_lending(lending, datetime.now().date())
            return render(request, 'lending_extended.html',
                          {'member': lending.member,
                           'item': item,
                           "date": lending.end_date
                           })
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
    print("Cannot extend")
    return redirect('/members/' + str(lending.member.pk))
