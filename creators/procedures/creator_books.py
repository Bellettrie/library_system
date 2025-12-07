from django.db.models import Q

from creators.models import Creator
from works.models import Work, WorkRelation, CreatorToWork
from search.query import query_annotate_and_sort_bookcodes


def get_books_for_author(creator: Creator):
    start_works = CreatorToWork.objects.filter(creator=creator)
    work_ids = []
    for work in start_works:
        work_ids.append(work.work.id)

    link_works = WorkRelation.RelationTraversal.author_matches(work_ids)
    for link_work in link_works:
        work_ids.append(link_work.to_work.id)
        work_ids.append(link_work.from_work.id)

    query = Work.objects.filter(id__in=set(work_ids))

    q = query_annotate_and_sort_bookcodes(query)
    return q.all()
