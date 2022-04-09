from datetime import datetime

from members.models import Member


def delete_member(member: Member):
    pass


def can_delete(member: Member, current_date: datetime.date) -> None:
    return True


def delete_or_except(member: Member, current_date : datetime.date):
    pass