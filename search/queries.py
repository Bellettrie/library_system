from django.db.models import Q

from book_code_generation.helpers import standardize_code, normalize_str


def filter_basic_text_get_q(words):
    if len(words) == 0:
        return None
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


def filter_basic_text(query, words):
    for q in filter_basic_text_get_q(words):
        query = query.filter(q)
    return query


def filter_author_text(query, words):
    for q in filter_basic_text_get_q(words):
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
    # We create a query to (at-once) select all works that have an item in a specific state.
    # Therefore we start by joining works with items
    # And then we join the item on it's most recent itemstate,
    # by using an inner query to fetch the maximum of the itemstate's datetimes.
    query = """
     COALESCE(
     (
     SELECT DISTINCT ON (wx.item_id)
        wx.type
    FROM
     works_itemstate as wx
        WHERE works_item.id = wx.item_id
         ORDER BY wx.item_id ASC, date_time DESC
     ), 'AVAILABLE') = ANY(%s)"""
    return q.extra(where=[query], params=[states])


def filter_book_code_get_q(word):
    ww = standardize_code(word.replace("*", ""))
    if word.startswith("*"):
        return Q(book_code__endswith=word) | Q(book_code_sortable__endswith=ww)
    elif word.endswith("*"):
        return Q(book_code__startswith=word) | Q(book_code_sortable__startswith=ww)
    else:
        return Q(book_code=word) | Q(book_code_sortable=ww)


def filter_location(query, categories):
    return query.filter(item__location__category__in=categories)
