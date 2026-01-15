from typing import Any

from django.db.models import Q, F
from django.db.models.expressions import RawSQL

from book_code_generation.helpers import standardize_code, normalize_str
from search.models.helpers import clean_word


def filter_basic_text_get_q(words):
    if len(words) == 0:
        return ""
    queries = []
    for word in words:
        query = single_word_cleanup(word)
        queries = queries + [query]

    return queries


def single_word_cleanup(word) -> Any:
    word = clean_word(word)

    if word.startswith("*"):
        return Q(wordmatch__word__word__endswith=word.replace("*", ""))
    elif word.endswith("*"):
        return Q(wordmatch__word__word__startswith=word.replace("*", ""))

    return Q(wordmatch__word__word=word)


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
