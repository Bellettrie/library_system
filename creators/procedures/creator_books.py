from django.db.models import Q

from creators.models import Creator
from series.models import Series, WorkInSeries
from works.models import Work, CreatorToWork, WorkRelation
from works.views import query_annotate_and_sort_bookcodes


def get_books_for_author(creator: Creator):
    series = set(Series.objects.filter(creatortoseries__creator=creator))
    series_len = 0
    while series_len < len(series):
        series_len = len(series)
        series = series | set(Series.objects.filter(part_of_series__in=series))

    work_series = WorkInSeries.objects.filter(part_of_series__in=series)

    start_works = CreatorToWork.objects.filter(creator=creator)
    work_ids = []
    for work in start_works:
        work_ids.append(work.work.id)

    link_works = WorkRelation.RelationTraversal.for_search_words_inverse(work_ids)
    for link_work in link_works:
        work_ids.append(link_work.from_work.id)
        work_ids.append(link_work.to_work.id)
    for ll in work_series:
        work_ids.append(ll.work.id)
    query = Work.objects.filter(id__in=work_ids)
    q = query_annotate_and_sort_bookcodes(query)
    return q.all()
