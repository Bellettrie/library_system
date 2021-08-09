from django.db.models import Q

from search.models import get_words_in_str
from works.models import Publication, ItemState, Location, Category


class SearchOp:
    def exec(self):
        return None


class BaseSearchQuery(SearchOp):
    def __init__(self, sentence):
        self.words = get_words_in_str(sentence)

    def exec(self):
        if len(self.words) == 0:
            return None
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
            return None
        res = None
        for word in self.words:
            if res is None:
                res = Publication.objects
            if word.startswith("*"):
                res = res.filter(Q(wordmatch__word__word__endswith=word.replace("*", "")) & Q(wordmatch__type="AUTHOR"))
            elif word.endswith("*"):
                res = res.filter(Q(wordmatch__word__word__startswith=word.replace("*", "")) & Q(wordmatch__type="AUTHOR"))
            else:
                res = res.filter(Q(wordmatch__word__word=word) & Q(wordmatch__type="AUTHOR"))
        return res


class SeriesSearchQuery(SearchOp):
    def __init__(self, sentence):
        self.words = get_words_in_str(sentence)

    def exec(self):
        if len(self.words) == 0:
            return None
        res = None
        for word in self.words:
            if res is None:
                res = Publication.objects
            if word.startswith("*"):
                res = res.filter(Q(wordmatch__word__word__endswith=word.replace("*", "")) & Q(wordmatch__type="SERIES"))
            elif word.endswith("*"):
                res = res.filter(Q(wordmatch__word__word__startswith=word.replace("*", "")) & Q(wordmatch__type="SERIES"))
            else:
                res = res.filter(Q(wordmatch__word__word=word) & Q(wordmatch__type="SERIES"))
        return res


class TitleSearchQuery(SearchOp):
    def __init__(self, sentence):
        self.words = get_words_in_str(sentence)

    def exec(self):
        if len(self.words) == 0:
            return None
        res = None
        for word in self.words:
            if res is None:
                res = Publication.objects
            if word.startswith("*"):
                res = res.filter(Q(wordmatch__word__word__endswith=word.replace("*", "")) & Q(Q(wordmatch__type="TITLE") | Q(wordmatch__type="SUBWORK")))
            elif word.endswith("*"):
                res = res.filter(Q(wordmatch__word__word__startswith=word.replace("*", "")) & Q(Q(wordmatch__type="TITLE") | Q(wordmatch__type="SUBWORK")))
            else:
                res = res.filter(Q(wordmatch__word__word=word) & Q(Q(wordmatch__type="TITLE") | Q(wordmatch__type="SUBWORK")))
        return res


class StateSearchQuery(SearchOp):
    def __init__(self, states: [str]):
        self.states = states

    def exec(self):
        if "AVAILABLE" in self.states:
            return None
        recent_states = dict()
        for item_state in ItemState.objects.all():
            state = recent_states.get(item_state.item_id, item_state)

            if item_state.dateTime >= state.dateTime:
                if item_state.type in self.states:
                    recent_states[item_state.item_id] = item_state
                elif item_state.dateTime > state.dateTime:
                    recent_states.pop(item_state.item_id)
        return Publication.objects.filter(item__itemstate__in=recent_states.values())


class BookCodeSearchQuery(SearchOp):
    def __init__(self, states: str):
        self.states = states

    def exec(self):
        print("II", self.states)
        res = None
        word = self.states
        if res is None:
            res = Publication.objects
        if word.startswith("*"):
            print("A")
            res = res.filter(Q(item__book_code_sortable__endswith=self.states.replace("*", "")) | Q(item__book_code__endswith=self.states.replace("*", "")))
        elif word.endswith("*"):
            print("B")
            res = res.filter(Q(item__book_code_sortable__startswith=self.states.replace("*", "")) | Q(item__book_code__startswith=self.states.replace("*", "")))
        else:
            print("C")
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
