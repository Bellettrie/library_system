from typing import Protocol

from django.db.models import QuerySet

from works.models import Work


class Sorter(Protocol):
    def sort_query(self, query: QuerySet[Work], asc: bool = True) -> QuerySet[Work]:
        pass


class BookCodeSorter(Sorter):
    def sort_query(self, query: QuerySet[Work], asc: bool = True) -> QuerySet[Work]:
        if asc:
            query = query.order_by("book_codeX", "id", 'itemid')
        else:
            query = query.order_by("-book_codeX", "-id", '-itemid')
        query = query.distinct("book_codeX", "id", 'itemid')
        return query
