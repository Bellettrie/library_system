from datetime import datetime, timedelta

from config.models import LendingSettings, Holiday
from lendings.models import Lending
from members.models import Member
from works.models import Item


def get_end_date(item: Item, member: Member, start_date: datetime.date):
    lending_settings = LendingSettings.get_for(item, member)
    result_date = start_date + timedelta(days=lending_settings.term)
    result_date = Holiday.get_handin_day_after_or_on(result_date)

    # Saturday: + 2 days, Sunday: +1 day
    if result_date.weekday() == 5:
        result_date += timedelta(days=2)
    if result_date.weekday() == 6:
        result_date += timedelta(days=1)

    return Holiday.get_handin_day_before_or_on(min(result_date, member.end_date))


def get_end_date_for_lending(lending: Lending, start_date: datetime.date):
    return get_end_date(lending.item, lending.member, start_date)
