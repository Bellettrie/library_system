from creators.models import Creator
from creators.procedures.get_all_author_aliases import get_all_author_aliases_by_ids
from works.models import Work, CreatorToWork, WorkRelation
from works.views import query_annotate_and_sort_bookcodes


def get_books_for_author(creator: Creator):
    creators = get_all_author_aliases_by_ids([creator.id])
    creator_works = CreatorToWork.objects.filter(creator__in=creators)
    works = map(lambda cw: cw.work_id, creator_works)
    wrs = WorkRelation.RelationTraversal.series_down(list(works))

    work_ids = []
    for wr in wrs:
        work_ids.append(wr.from_work_id)
        work_ids.append(wr.to_work_id)

    query = Work.objects.filter(id__in=set(work_ids))
    return query_annotate_and_sort_bookcodes(query)
