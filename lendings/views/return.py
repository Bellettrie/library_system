from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from works.models import Item


@transaction.atomic
@permission_required('lendings.return')
def return_book(request, work_id):
    item = get_object_or_404(Item, pk=work_id)
    lending = item.current_lending()
    late_days = datetime.now().date() - lending.end_date
    if request.method == 'POST':
        register_returned(lending, request.user.member)
        return redirect('/members/' + str(lending.member.pk))  # TODO intermediate page
    return render(request, 'return_book.html', {'item': item, 'lending': lending,
                                                'late': lending.end_date < datetime.now().date(),
                                                'days_late': late_days.days,
                                                'fine': lending.calculate_fine()})
