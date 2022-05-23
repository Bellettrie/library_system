from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from utils.time import get_today
from works.models import Item
from lendings.procedures.register_returned import register_returned_with_mail


@transaction.atomic
@permission_required('lendings.return')
def return_item(request, work_id):
    item = get_object_or_404(Item, pk=work_id)
    lending = item.current_lending()
    late_days = get_today() - lending.end_date
    if request.method == 'POST':
        register_returned_with_mail(lending, request.user.member)
        return redirect('/members/' + str(lending.member.pk))
    return render(request, 'return_book.html', {'item': item, 'lending': lending,
                                                'late': lending.end_date < get_today(),
                                                'days_late': late_days.days,
                                                'fine': lending.calculate_fine()})
