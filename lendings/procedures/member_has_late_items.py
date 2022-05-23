from datetime import datetime

from members.models import Member
from utils.time import get_today


def member_has_late_items(member: Member, current_date=None):
    current_date = current_date or get_today()

    from lendings.models import Lending
    from works.models import ItemType, Category

    lendings = Lending.objects.filter(member=member, handed_in=False)

    for lending in lendings:
        if lending.is_late(current_date):
            return True
    return False
