from datetime import datetime

from members.models import Member, MembershipPeriod

FUTURE = datetime.date(datetime.fromisoformat('9999-01-01'))


def overlaps(start_a, end_a, start_b, end_b):
    start_a = start_a or datetime.date(datetime.fromisoformat('1900-01-01'))
    start_b = start_b or datetime.date(datetime.fromisoformat('1900-01-01'))
    end_a = end_a or datetime.date(datetime.fromisoformat('2100-01-01'))
    end_b = end_b or datetime.date(datetime.fromisoformat('2100-01-01'))
    return (start_a <= end_b) and (end_a >= start_b)


def delete_double_periods(member: Member):
    to_delete = set()

    for msp in MembershipPeriod.objects.filter(member=member):
        for msp2 in MembershipPeriod.objects.filter(member=member):
            if msp != msp2 and msp2 not in to_delete and msp not in to_delete and overlaps(msp.start_date,
                                                                                           msp.end_date,
                                                                                           msp2.start_date,
                                                                                           msp2.end_date):
                if msp.member_background == msp2.member_background and msp.membership_type == msp2.membership_type:
                    msp.start_date = min(msp.start_date or FUTURE, msp2.start_date or FUTURE)

                    msp.end_date = max(msp.end_date or FUTURE, msp2.end_date or FUTURE)
                    if msp.start_date == FUTURE:
                        msp.start_date = None
                    if msp.end_date == FUTURE:
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
