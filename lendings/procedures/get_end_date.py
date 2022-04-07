from datetime import datetime, timedelta

from config.models import LendingSettings, Holiday
from lendings.models import Lending
from members.models import Member
from works.models import Item


def get_end_date(item: Item, member: Member, start_date: datetime.date):
    lending_settings = LendingSettings.get_for(item, member)
    result_date = start_date + timedelta(days=lending_settings.term)
    result_date = Holiday.get_handin_day_after_or_on(result_date)
    membership_period =  member.get_current_membership_period(start_date)
    end_date = None
    if not membership_period:
        end_date = datetime.date(datetime(1900,1,1))
    elif membership_period.end_date is not None:
        end_date = membership_period.end_date
    else:
        end_date = datetime.date(datetime(9999,1,1))

    result_date = min(result_date, end_date)

    return Holiday.get_handin_day_before_or_on(result_date)


def get_end_date_for_lending(lending: Lending, start_date: datetime.date):
    return get_end_date(lending.item, lending.member, start_date)
