from django.db.models import Q

from search.models import get_words_in_str
from works.models import Publication, ItemState, Category, Item


class SearchOp:
    def exec(self):
        return Publication.objects.none()


class BaseSearchQuery(SearchOp):
    def __init__(self, sentence):
        self.words = get_words_in_str(sentence)

    def exec(self):
        if len(self.words) == 0:
            return Publication.objects.none()
        res = None
        for word in self.words:
            if res is None:
                res = Publication.objects
            if word.startswith("*"):
                res = res.filter(wordmatch__word__word__endswith=word.replace("*", ""))
            elif word.endswith("*"):
                res = res.filter(wordmatch__word__word__startswith=word.replace("*", ""))
            else:
                res = res.filter(wordmatch__word__word=word)
        return res


class AuthorSearchQuery(SearchOp):
    def __init__(self, sentence):
        self.words = get_words_in_str(sentence)

    def exec(self):
        if len(self.words) == 0:
            return Publication.objects.none()
        res = None
        for word in self.words:
            if res is None:
                res = Publication.objects
            if word.startswith("*"):
                res = res.filter(Q(wordmatch__word__word__endswith=word.replace("*", "")) & Q(wordmatch__type="AUTHOR"))
            elif word.endswith("*"):
                res = res.filter(
                    Q(wordmatch__word__word__startswith=word.replace("*", "")) & Q(wordmatch__type="AUTHOR"))
            else:
                res = res.filter(Q(wordmatch__word__word=word) & Q(wordmatch__type="AUTHOR"))
        return res


class SeriesSearchQuery(SearchOp):
    def __init__(self, sentence):
        self.words = get_words_in_str(sentence)

    def exec(self):
        if len(self.words) == 0:
            return Publication.objects.none()
        res = None
        for word in self.words:
            if res is None:
                res = Publication.objects
            if word.startswith("*"):
                res = res.filter(Q(wordmatch__word__word__endswith=word.replace("*", "")) & Q(wordmatch__type="SERIES"))
            elif word.endswith("*"):
                res = res.filter(
                    Q(wordmatch__word__word__startswith=word.replace("*", "")) & Q(wordmatch__type="SERIES"))
            else:
                res = res.filter(Q(wordmatch__word__word=word) & Q(wordmatch__type="SERIES"))
        return res


class TitleSearchQuery(SearchOp):
    def __init__(self, sentence):
        self.words = get_words_in_str(sentence)

    def exec(self):
        if len(self.words) == 0:
            return Publication.objects.none()
        res = None
        for word in self.words:
            if res is None:
                res = Publication.objects
            if word.startswith("*"):
                res = res.filter(Q(wordmatch__word__word__endswith=word.replace("*", "")) & Q(
                    Q(wordmatch__type="TITLE") | Q(wordmatch__type="SUBWORK")))
            elif word.endswith("*"):
                res = res.filter(Q(wordmatch__word__word__startswith=word.replace("*", "")) & Q(
                    Q(wordmatch__type="TITLE") | Q(wordmatch__type="SUBWORK")))
            else:
                res = res.filter(
                    Q(wordmatch__word__word=word) & Q(Q(wordmatch__type="TITLE") | Q(wordmatch__type="SUBWORK")))
        return res


def search_state(states):
    if "AVAILABLE" in states:
        return None
    r = (Publication.objects.raw(
        "SELECT work_ptr_id from works_publication left join works_item ON works_publication.work_ptr_id=works_item.publication_id LEFT JOIN works_itemstate as wx " +
        "ON works_item.id = wx.item_id " +
        "WHERE date_time = " +
        "(SELECT MAX(w.date_time) FROM works_itemstate as w " +
        "where w.item_id=wx.item_id AND wx.type IN %s);", states))
    return r
class StateSearchQuery(SearchOp):
    def __init__(self, states: [str]):
        self.states = states

    def exec(self):


        return r


class BookCodeSearchQuery(SearchOp):
    def __init__(self, states: str):
        self.states = states

    def exec(self):
        res = None
        word = self.states
        if res is None:
            res = Publication.objects
        if word.startswith("*"):
            res = res.filter(Q(item__book_code_sortable__endswith=self.states.replace("*", "")) | Q(
                item__book_code__endswith=self.states.replace("*", "")))
        elif word.endswith("*"):
            res = res.filter(Q(item__book_code_sortable__startswith=self.states.replace("*", "")) | Q(
                item__book_code__startswith=self.states.replace("*", "")))
        else:
            res = res.filter(Q(item__book_code_sortable=self.states) | Q(item__book_code=self.states))

        return res


class LocationSearchQuery(SearchOp):
    def __init__(self, categories: [Category]):
        self.categories = categories

    def exec(self):
        return Publication.objects.filter(item__location__category__in=self.categories)


class OrOp(SearchOp):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def exec(self):
        return self.left.exec() | self.right.exec()


class AndOp(SearchOp):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def exec(self):
        return self.left.exec() & self.right.exec()
