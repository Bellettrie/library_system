from datetime import datetime


def get_fine_days_for(item, member, end_date: datetime.date, current_date: datetime.date):
    return max(0, (current_date-end_date ).days)  # TODO: omit holiday days


def get_fine_days(lending, current_date: datetime.date):
    return get_fine_days_for(lending.item, lending.member, lending.end_date, current_date)
