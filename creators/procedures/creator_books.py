from django.db.models import Q

from creators.models import Creator
from series.models import Series
from works.models import Publication


def get_books_for_author(creator:Creator):
    series = set(Series.objects.filter(creatortoseries__creator=creator))
    series_len = 0
    while series_len < len(series):
        series_len = len(series)
        series = series | set(Series.objects.filter(part_of_series__in=series))

    work_set = set()
    for work in Publication.objects.filter(
            Q(creatortowork__creator=creator) | Q(workinseries__part_of_series__in=series) | Q(workinpublication__work__creatortowork__creator=creator)):
            work_set.add(work)

    result = []
    for item in work_set:
        result.append(item)
    return result