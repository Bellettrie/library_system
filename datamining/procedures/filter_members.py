import logging

from django.db.models import Q

from members.models import Member


def filter_members_by_committees(found_committees):
    committees = list(map(lambda it: int(it), found_committees))
    if len(committees) > 0:
        query = Q(committees__pk__in=committees) & Q(is_anonymous_user=False)
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

    query = membership_period_filter & Q(is_anonymous_user=False)

    members = Member.objects.filter(query).distinct()
    return members


def filter_members_by_privacy_option(option: str):
    if option == "activities":
        memberList = Member.objects.filter(privacy_activities=True, is_anonymous_user=False).all()
        result = []
        for member in memberList:
            # TODO: something with last year?
            if member.is_currently_member():
                result.append(member)
        return result
    if option == "publications":
        memberList = Member.objects.filter(privacy_publications=True, is_anonymous_user=False).all()
        result = []
        for member in memberList:
            # TODO: something with last year?
            if member.is_currently_member():
                result.append(member)
        return result
    if option == "reunions":
        return Member.objects.filter(privacy_reunions=True, is_anonymous_user=False).all()
    logging.debug("wrong option", option)
    return []


def filter_members_missing_dms():
    memberList = Member.objects.filter(Q(dms_registered=False) & Q(is_anonymous_user=False)).all()
    result = []
    for member in memberList:
        if member.membership_type and member.membership_type.needs_union_card:
            result.append(member)
    return result