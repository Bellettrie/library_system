from django.db.models import Q

from creators.models import Creator
from series.models import Series
from works.models import Publication


def get_books_for_author(creator: Creator):
    series = set(Series.objects.filter(creatortoseries__creator=creator))
    series_len = 0
    while series_len < len(series):
        series_len = len(series)
        series = series | set(Series.objects.filter(part_of_series__in=series))

    return Publication.objects.filter(
        Q(creatortowork__creator=creator) | Q(workinseries__part_of_series__in=series) | Q(
            workinpublication__work__creatortowork__creator=creator)).order_by("title","id").prefetch_related(
        "item_set").distinct("title","id").all()
