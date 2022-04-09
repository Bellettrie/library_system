from fines.models import Fine
from lendings.procedures.get_total_fine import get_total_fine_for_lending


def register_fine_for_returned(lending, now, paid):
    fine = get_total_fine_for_lending(lending, now)
    if fine > 0:
        Fine.objects.create(paid=paid, lending=lending, amount=get_total_fine_for_lending(lending, now),
                            return_date=now)
