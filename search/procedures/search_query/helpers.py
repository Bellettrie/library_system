from django.db.models import Q, F
from django.db.models.expressions import RawSQL

from book_code_generation.helpers import standardize_code, normalize_str


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


def query_annotate(query):
    query = query.annotate(
        itemid=F('item__id'),
        book_code_sortable=F('item__book_code_sortable'),
        book_code=F('item__book_code'),
        book_code_extension=F('item__book_code_extension'),
        is_series_bookcode_sortable=F('seriesv2__book_code_sortable'),
        book_codeX=RawSQL('coalesce(works_item.book_code_sortable,series_seriesv2.book_code_sortable)', []),
    )
    return query
