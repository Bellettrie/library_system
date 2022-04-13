from datetime import datetime

from members.models import Member


def delete_member(member: Member):
    pass


def can_delete(member: Member, current_date: datetime.date) -> None:
    """
    :param member: member to be deleted
    :param current_date: date on which to be deleted
    :return: None
    :except ...: Raise exception if ...
    """
    return True


def delete_or_except(member: Member, current_date: datetime.date):
    can_delete(member, current_date)
    delete_member(member)
