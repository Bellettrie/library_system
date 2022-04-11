from _datetime import datetime

from config.models import Holiday
from lendings.models import Lending


def get_fine_days(lending: Lending, current_date: datetime.date):
    """
    Calculate the number of days the person is late.
    :param lending: what lending to calculate the number of fine days for
    :param current_date: what is the current date?
    :return: The number of days the lending is late. 0 if the lending is not late.
    """
    return Holiday.get_number_of_fine_days_between(lending.end_date, current_date)
