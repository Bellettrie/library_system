from lendings.models import Lending
from lendings.procedures.get_end_date import get_end_date_for_lending


def extend_lending(lending: Lending, now):
    """Extend existing lending. Throws exception if book cannot be extended.
    :param lending: the lending to be extended
    :param now: what is the date on which the lending is extended?
    :return: None
    //TODO: Apply same clean code practices from lend to extend
    """

    lending.end_date = get_end_date_for_lending(lending, now)
    lending.last_extended = now
    lending.times_extended = lending.times_extended + 1
    lending.save()
