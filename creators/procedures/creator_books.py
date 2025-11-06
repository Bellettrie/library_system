from django.db.models import Q

from creators.models import Creator
from series.models import Series
from works.models import Work
from works.views import query_annotate_and_sort_bookcodes


def get_books_for_author(creator: Creator):
    series = set(Series.objects.filter(creatortoseries__creator=creator))
    series_len = 0
    while series_len < len(series):
        series_len = len(series)
        series = series | set(Series.objects.filter(part_of_series__in=series))

    query = (
        Work.objects.filter(
            Q(creatortowork__creator=creator)
            | Q(workinseries__part_of_series__in=series)
            | Q(work_in_publication_root__work__creatortowork__creator=creator)
        )
    )

    q = query_annotate_and_sort_bookcodes(query)
    return q.all()
