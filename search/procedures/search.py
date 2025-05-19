from typing import Protocol

from django.db.models import QuerySet

from search.models import SearchRecord


class SearchTerm(Protocol):
    def filter(self, query: QuerySet)-> QuerySet:
        return query
    def order (self, query: QuerySet)-> QuerySet:
        return query

def search(targets=None, offset=0, *queries: SearchTerm) ->QuerySet:
    if targets is None:
        targets = ["member", "creator", "series", "item"]

    q = SearchRecord.objects.all()
    for query in queries:
        q = query.filter(q)
    for query in queries:
        q = query.order(q)

    return q