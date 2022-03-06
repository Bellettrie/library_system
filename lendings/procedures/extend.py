from lendings.models import Lending


def extend_lending(lending: Lending, now):
    from lendings.procedures.get_end_date import get_end_date

    lending.end_date = get_end_date(lending.item, lending.member, now)
    lending.last_extended = now
    lending.times_extended = lending.times_extended + 1
    lending.save()
