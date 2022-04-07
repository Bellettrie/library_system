from datetime import datetime, timedelta

from config.models import LendingSettings, Holiday
from lendings.models import Lending
from members.models import Member
from works.models import Item


def get_end_date(item: Item, member: Member, start_date: datetime.date):
    """
    Get how long an item could be lent by a specific member, given a starting date.
    This function takes into account the member type, membership periods, and holidays.
    :param item: The item for which to calculate an end-date for a lending
    :param member: The member who wants to obtain the item
    :param start_date: The expected start date for the lending
    :return: datetime.date: end-date as calculated
    """
    lending_settings = LendingSettings.get_for(item, member)
    result_date = start_date + timedelta(days=lending_settings.term)
    result_date = Holiday.get_handin_day_after_or_on(result_date)
    membership_period =  member.get_current_membership_period(start_date)

    end_date = None
    while True:
        if not membership_period:
            end_date =  end_date or datetime.date(datetime(1900,1,1))
            break
        elif membership_period.end_date is not None:
            end_date = membership_period.end_date
        else:
            end_date = datetime.date(datetime(9999,1,1))
            break
        if end_date > result_date:
            break
        membership_period =  member.get_current_membership_period(end_date+timedelta(days=1))

    result_date = min(result_date, end_date)

    return Holiday.get_handin_day_before_or_on(result_date)


def get_end_date_for_lending(lending: Lending, start_date: datetime.date):
    """
        Calculate a new end-date for an existing lending.
        Used for:
        1. re-calculate end-days when a holiday is added
        2. extending books
        :param lending: the Lending for which to calculate a new end date
        :param start_date: The expected start date for the lending
        :return: datetime.date: end-date as calculated
    """
    return get_end_date(lending.item, lending.member, start_date)
