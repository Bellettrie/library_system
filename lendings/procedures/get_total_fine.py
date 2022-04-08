from datetime import datetime

from config.models import LendingSettings
from lendings.models import Lending
from lendings.procedures.get_fine_days import get_fine_days


def get_total_fine_for_lending(lending: Lending, current_date: datetime.date):
    """
    Calculate the fine on a lending
    :param lending: Which lending to calculate the fine for
    :param current_date: On which date?
    :return: Fine, in eurocents
    """
    lending_settings = LendingSettings.get_for(lending.item, lending.member)

    return min(lending_settings.max_fine, lending_settings.fine_amount * get_fine_days(lending, current_date))
