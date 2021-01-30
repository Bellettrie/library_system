from datetime import datetime, date

from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand
from members.models import Committee, Member, MembershipPeriod, MemberBackground, MembershipType
PAST = datetime.date(datetime.fromisoformat('1900-01-01'))
FUTURE = datetime.date(datetime.fromisoformat('2100-01-01'))

def overlaps(startA, endA, startB, endB):
    startA = startA or datetime.date(datetime.fromisoformat('1900-01-01'))
    startB = startB or datetime.date(datetime.fromisoformat('1900-01-01'))
    endA = endA or datetime.date(datetime.fromisoformat('2100-01-01'))
    endB = endB or datetime.date(datetime.fromisoformat('2100-01-01'))

    return (startA <= endB) and (endA >= startB)


def mig():
    to_delete = set()
    for member in Member.objects.all():
        for msp in MembershipPeriod.objects.filter(member=member):
            for msp2 in MembershipPeriod.objects.filter(member=member):
                if msp != msp2 and msp2 not in to_delete and msp not in to_delete and overlaps(msp.start_date, msp.end_date, msp2.start_date, msp2.end_date):
                    if msp.member_background == msp2.member_background and msp.membership_type == msp2.membership_type:
                        msp.start_date = min(msp.start_date or FUTURE, msp2.start_date or FUTURE)

                        msp.end_date = max(msp.end_date or FUTURE, msp2.end_date or FUTURE)
                        if msp.start_date == FUTURE:
                            msp.start_date = None
                        if msp.end_date == PAST:
                            msp.end_date = None
                        msp.save()
                        to_delete.add(msp2)
                    else:
                        if msp.start_date < msp2.start_date:
                            msp.end_date = msp2.start_date
                        else:
                            msp2.end_date = msp.start_date
                        msp.save()
                        msp2.save()
                        if msp.end_date and msp.start_date >= msp.end_date:
                            to_delete.add(msp)
                        if msp2.end_date and msp2.start_date >= msp2.end_date:
                            to_delete.add(msp2)
    for z in to_delete:
        z.delete()


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        mig()
