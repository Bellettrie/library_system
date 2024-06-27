from django.db.models import Q

from members.models import Member

def filter_members_by_committees(found_committees):
    committees = list(map(lambda it: int(it), found_committees))
    if len(committees) > 0:
        query = Q(committees__pk__in=committees)
        members = Member.objects.filter(query).distinct()
        return members
    else:
        return Member.objects.none()


def filter_members_by_date(on, include_honorary):
    # membership period checks
    after_part = Q(membershipperiod__start_date__lte=on)
    before_part = Q(membershipperiod__end_date__gte=on)
    before_part_honorary = Q(membershipperiod__end_date__isnull=True)

    membership_period_filter = after_part & before_part
    if include_honorary:
        membership_period_filter = after_part & (before_part | before_part_honorary)

    query = membership_period_filter

    members = Member.objects.filter(query).distinct()
    return members
