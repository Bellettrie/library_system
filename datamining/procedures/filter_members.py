from django.db.models import Q

from members.models import Member


def filter_members(found_committees, found_privacy_settings, on, include_honorary, only_blacklisted, dms):
    # membership period checks
    after_query = Q(membershipperiod__start_date__lte=on)
    before_query = Q(membershipperiod__end_date__gte=on)
    before_query_honorary = Q(membershipperiod__end_date__isnull=True)
    query = after_query
    combined_before_query_honorary = before_query
    if include_honorary:
        combined_before_query_honorary = (before_query | before_query_honorary)

    if query is None:
        query = combined_before_query_honorary
    else:
        query = query & combined_before_query_honorary

    # simple checks
    if dms:
        query = query & Q(dms_registered=False)

    if 'activities' in found_privacy_settings:
        query = query & Q(privacy_activities=True)
    if 'publications' in found_privacy_settings:
        query = query & Q(privacy_publications=True)
    if 'reunions' in found_privacy_settings:
        query = query & Q(privacy_reunions=True)

    if only_blacklisted:
        query = query & Q(is_blacklisted=True)

    committees = list(map(lambda it: int(it), found_committees))
    if len(committees) > 0:
        query = query & Q(committees__pk__in=committees)

    members = Member.objects.filter(query).distinct()
    return members
