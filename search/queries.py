from django.db.models import Q

from works.models import  Category


def get_basic_text_search(words):
        if len(words) == 0:
            return None
        full_query = None
        for word in words:
            if word.startswith("*"):
                next_query_part = Q(wordmatch__word__word__endswith=word.replace("*", ""))

            elif word.endswith("*"):
                next_query_part = Q(wordmatch__word__word__startswith=word.replace("*", ""))
            else:
                next_query_part = Q(wordmatch__word__word=word)

            if full_query is None:
                full_query = next_query_part
            else:
                full_query = full_query & next_query_part
        print(full_query)
        return full_query


def get_author_text_search(words):
        return get_basic_text_search(words) & Q(wordmatch__type="AUTHOR")

def get_series_text_search(words):
    return get_basic_text_search(words) & Q(wordmatch__type="SERIES")

def get_title_text_search(words):
    return get_basic_text_search(words) & Q(Q(wordmatch__type="TITLE") | Q(wordmatch__type="SUBWORK"))



def search_state(q, states):
    # Shortcut, because 'available' is not a state on which we can search.
    if "AVAILABLE" in states or len(states) == 0:
        return q
    # We create a query to (at-once) select all works that have an item in a specific state.
    # Therefore we start by joining works with items
    # And then we join the item on it's most recent itemstate,
    # by using an inner query to fetch the maximum of the itemstate's datetimes.
    query = """
works_work.id IN (SELECT
    works_work.id
FROM
    works_work
INNER JOIN
    works_item
        ON works_work.id = works_item.publication_id
    JOIN works_itemstate as wx
        ON works_item.id = wx.item_id
        WHERE date_time =
        (SELECT
            MAX(w.date_time)
         FROM works_itemstate as w
         WHERE w.item_id = wx.item_id AND wx.type = any(%s)
     ))"""
    return q.extra(where=[query], params=[states])


def get_book_code_search_subquery(word):
    if word.startswith("*"):
        return Q(item__book_code_sortable__endswith=word.replace("*", "")) | Q(
            item__book_code__endswith=word.replace("*", ""))
    elif word.endswith("*"):
        return Q(item__book_code_sortable__startswith=word.replace("*", "")) | Q(
            item__book_code__startswith=word.replace("*", ""))
    else:
        return Q(item__book_code_sortable=word) | Q(item__book_code=word)



class LocationSearchQuery:
    def __init__(self, categories: [Category]):
        self.categories = categories

    def exec(self):
        return Q(item__location__category__in=self.categories)



class AndOp:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def exec(self):
        return self.left.exec() & self.right.exec()
