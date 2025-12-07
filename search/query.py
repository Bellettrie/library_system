from typing import Protocol

from django.db.models import QuerySet, F
from django.db.models.expressions import RawSQL

from search.queries import Filter, StatesFilter
from works.models import Work
from works.models.item_state import get_available_states


class SearchQuery:
    class ResultBase(Protocol):
        def finish_query(self, query: QuerySet[Work]) -> QuerySet[Work]:
            pass

    class CurrentItemsOnly(ResultBase):
        def finish_query(self, query: QuerySet[Work]) -> QuerySet[Work]:
            return query.filter(itemid__isnull=False)
        
    class CurrentAvailableItemsOnly(ResultBase):
        def finish_query(self, query: QuerySet[Work]) -> QuerySet[Work]:
            statz = get_available_states()
            sf = StatesFilter(list(map(lambda state: state.state_name, statz)))
            query = sf.filter(query)
            return SearchQuery.CurrentItemsOnly().finish_query(query)

    class AllWorks(ResultBase):
        def finish_query(self, query: QuerySet[Work]) -> QuerySet[Work]:
            return query

    def __init__(self,
                 result_base: ResultBase):
        self.filters = []
        self.result_base = result_base

    def add_filter(self, f: Filter):
        self.filters.append(f)

    def search(self) -> QuerySet[Work]:
        if len(self.filters) == 0:
            return Work.objects.none()
        query = Work.objects
        query = query_annotate_and_sort_bookcodes(query)
        for f in self.filters:
            query = f.filter(query)

        query = self.result_base.finish_query(query)

        return query.prefetch_related('creatortowork_set', "creatortowork_set__creator")


def query_annotate_and_sort_bookcodes(query):
    query = query.annotate(
        itemid=F('item__id'),
        book_code_sortable=F('item__book_code_sortable'),
        book_code=F('item__book_code'),
        book_code_extension=F('item__book_code_extension'),
        is_series_bookcode_sortable=F('seriesv2__book_code_sortable'),
        book_codeX=RawSQL('coalesce(works_item.book_code_sortable,series_seriesv2.book_code_sortable)', []),
    )
    query = query.order_by("book_codeX", "id", 'itemid')
    query = query.distinct("book_codeX", "id", 'itemid')
    return query
