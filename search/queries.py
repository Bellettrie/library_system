from typing import Protocol

from django.db.models import Q, QuerySet
from book_code_generation.helpers import standardize_code, normalize_str
from works.models import Work


def filter_book_code(word):
    ww = standardize_code(word.replace("*", ""))
    if word.startswith("*"):
        return Q(item__book_code__endswith=word) | Q(item__book_code_sortable__endswith=ww)
    elif word.endswith("*"):
        return Q(item__book_code__startswith=word) | Q(item__book_code_sortable__startswith=ww)
    else:
        return Q(item__book_code=word) | Q(item__book_code_sortable=ww)


def filter_basic_text_get_q(words):
    if len(words) == 0:
        return ""
    queries = []
    for word in words:
        word = normalize_str(word)
        if word.startswith("*"):
            next_query_part = Q(wordmatch__word__word__endswith=word.replace("*", ""))
        elif word.endswith("*"):
            next_query_part = Q(wordmatch__word__word__startswith=word.replace("*", ""))
        else:
            next_query_part = Q(wordmatch__word__word=word)
        queries = queries + [next_query_part]
    return queries


class Filter(Protocol):
    def filter(self, query: QuerySet[Work]) -> QuerySet[Work]:
        pass


class TitleFilter(Filter):
    def __init__(self, words):
        self.words = words

    def filter(self, query: QuerySet[Work]) -> QuerySet[Work]:
        for q in filter_basic_text_get_q(self.words):
            query = query.filter(Q(q & Q(wordmatch__type="TITLE") | Q(wordmatch__type="SUBWORK")))
        return query


class CreatorFilter(Filter):
    def __init__(self, words):
        self.words = words

    def filter(self, query: QuerySet[Work]) -> QuerySet[Work]:
        for q in filter_basic_text_get_q(self.words):
            query = query.filter(Q(q & Q(Q(wordmatch__type="CREATOR")| Q(wordmatch__type="AUTHOR"))))
        return query


class BookCodeFilter(Filter):
    def __init__(self, book_code):
        self.book_code = book_code

    def filter(self, query: QuerySet[Work]) -> QuerySet[Work]:
        return query.filter(filter_book_code(self.book_code))


class AnyWordFilter(Filter):
    def __init__(self, words):
        self.words = words

    def __filter_basic_text(self):
        qq = None
        for q in filter_basic_text_get_q(self.words):
            if qq is None:
                qq = q
            else:
                qq = qq & q
        return qq

    def filter(self, query: QuerySet[Work]) -> QuerySet[Work]:
        if len(self.words) == 1:
            fbc = filter_book_code(self.words[0])
            fbt = self.__filter_basic_text()
            return query.filter(fbc | fbt)
        else:
            return query.filter(self.__filter_basic_text())


class SeriesFilter(Filter):
    def __init__(self, words):
        self.words = words

    def filter(self, query: QuerySet[Work]) -> QuerySet[Work]:
        for q in filter_basic_text_get_q(self.words):
            query = query.filter(Q(q & Q(wordmatch__type="SERIES")))
        return query


class StatesFilter(Filter):
    def __init__(self, states):
        self.states = states

    def filter(self, query: QuerySet[Work]) -> QuerySet[Work]:
        # We find the type of the latest itemstate for the item.
        # If there's none, then the coalesce takes the second value: 'AVAILABLE'.
        raw_query = """
             COALESCE(
             (
             SELECT DISTINCT ON (wx.item_id)
                wx.type
            FROM
             works_itemstate as wx
                WHERE works_item.id = wx.item_id
                 ORDER BY wx.item_id ASC, date_time DESC
             ), 'AVAILABLE') = ANY(%s)"""
        return query.extra(where=[raw_query], params=[self.states])


class CategoriesFilter(Filter):
    def __init__(self, categories):
        self.categories = categories

    def filter(self, query: QuerySet[Work]) -> QuerySet[Work]:
        return query.filter(item__location__category__in=self.categories)
