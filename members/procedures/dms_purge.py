from members.models import Member
from utils.time import get_today


def dms_purge(now=None):
    counter = 0
    if now is None:
        now = get_today()
    for member in Member.objects.all():
        membership_period = member.get_current_membership_period(now)
        if membership_period is not None:
            if membership_period.end_date is None:
                continue
        member.dms_registered = False
        member.save()
        counter += 1
