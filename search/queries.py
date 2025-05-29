from django.db.models import Q


def filter_basic_text_get_q(words):
    if len(words) == 0:
        return None
    queries = []
    for word in words:
        if word.startswith("*"):
            next_query_part = Q(wordmatch__word__word__endswith=word.replace("*", ""))

        elif word.endswith("*"):
            next_query_part = Q(wordmatch__word__word__startswith=word.replace("*", ""))
        else:
            next_query_part = Q(wordmatch__word__word=word)
        queries = queries + [next_query_part]
    return queries


def filter_basic_text(query, words):
    for q in filter_basic_text_get_q( words):
        query = query.filter(q)
    return query


def filter_author_text(query, words):
    for q in filter_basic_text_get_q( words):
        query = query.filter(q)
    return query.filter(wordmatch__type="AUTHOR")


def filter_series_text(query, words):
    for q in filter_basic_text_get_q(words):
        query = query.filter(q)
    return query.filter(wordmatch__type="SERIES")


def filter_title_text(query, words):
    for q in filter_basic_text_get_q(words):
        query = query.filter(q)
    return query.filter(Q(wordmatch__type="TITLE") | Q(wordmatch__type="SUBWORK"))


def filter_state(q, states):
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


def filter_book_code_get_q(word):
    if word.startswith("*"):
        return Q(item__book_code_sortable__endswith=word.replace("*", "")) | Q(
            item__book_code__endswith=word.replace("*", ""))
    elif word.endswith("*"):
        return Q(item__book_code_sortable__startswith=word.replace("*", "")) | Q(
            item__book_code__startswith=word.replace("*", ""))
    else:
        return Q(item__book_code_sortable=word) | Q(item__book_code=word)

def filter_location(query, categories):
    return query.filter(item__location__category__in=categories)
