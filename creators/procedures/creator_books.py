from django.db.models import QuerySet

from creators.models import Creator
from works.models import Work, WorkRelation, CreatorToWork
from search.procedures.search_query.search_query import SearchQuery


class CreatorFilter:
    def __init__(self, creator):
        self.creator = creator

    def filter(self, query: QuerySet[Work]) -> QuerySet[Work]:
        start_works = CreatorToWork.objects.filter(creator=self.creator)
        work_ids = []
        for work in start_works:
            work_ids.append(work.work.id)

        link_works = WorkRelation.RelationTraversal.author_matches(work_ids)
        for link_work in link_works:
            work_ids.append(link_work.to_work.id)
            work_ids.append(link_work.from_work.id)

        return query.filter(id__in=work_ids)


def get_books_for_author(creator: Creator):
    sq = SearchQuery()
    sq.add_filter(CreatorFilter(creator))

    return sq.search().all()
