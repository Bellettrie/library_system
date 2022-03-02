from datetime import datetime, timedelta

from config.models import LendingSettings, Holiday
from lendings.models import Lending
from members.models import Member
from works.models import Item


def get_end_date(item: Item, member: Member, start_date: datetime.date):
    lending_settings = LendingSettings.get_for(item, member)
    result_date =  start_date + timedelta(days=lending_settings.term)
    result_date = Holiday.get_handin_day_after_or_on(result_date)
    return min(result_date, member.end_date)


def get_end_date_for_lending(lending: Lending, start_date: datetime.date):
    return get_end_date(lending.item, lending.member, start_date)