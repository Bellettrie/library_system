from typing import Protocol

from django.db.models import QuerySet

from search.procedures.search_query.helpers import query_annotate
from search.procedures.search_query.filters import Filter
from search.procedures.search_query.query_results import ResultBase, AllWorks
from search.procedures.search_query.sorters import BookCodeSorter, Sorter
from works.models import Work


class SearchQuery:
    def __init__(self,
                 result_base: ResultBase = AllWorks(), sorter: Sorter = BookCodeSorter()):
        self.filters = []
        self.result_base = result_base
        self.sorter = sorter

    def add_filter(self, f: Filter):
        self.filters.append(f)

    def set_result_base(self, result_base: ResultBase):
        self.result_base = result_base

    def set_sorter(self, sorter: Sorter):
        self.sorter = sorter

    def search(self) -> QuerySet[Work]:
        if len(self.filters) == 0:
            return Work.objects.none()
        query = Work.objects
        query = query_annotate(query)
        for f in self.filters:
            query = f.filter(query)

        query = self.result_base.finish_query(query)
        query = self.sorter.sort_query(query)

        return query.prefetch_related('creatortowork_set', "creatortowork_set__creator")
