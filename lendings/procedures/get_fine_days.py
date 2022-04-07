from datetime import datetime

from lendings.models import Lending


def get_fine_days(lending: Lending, current_date: datetime.date):
    """
    Calculate the number of days the person is late.
    :param lending: what lending to calculate the number of fine days for
    :param current_date: what is the current date?
    :return: The number of days the lending is late. 0 if the lending is not late.
    """
    return max(0, (current_date - lending.end_date).days)  # TODO: omit holiday days
