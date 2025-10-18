from django.db.models import QuerySet, F, Q

from search.queries import filter_book_code_get_q, filter_basic_text, filter_basic_text_get_q, filter_author_text, \
    filter_title_text, filter_series_text, filter_location, filter_state
from utils.get_query_words import get_query_words
from works.models import Work


def get_works(request):
    if request.GET.get('q', "").count("*") + \
            request.GET.get('q_author', "").count("*") + \
            request.GET.get('q_series', "").count("*") + \
            request.GET.get('q_title', "").count("*") + \
            request.GET.get('q_bookcode', "").count("*") > 3:
        raise ValueError("That's too much for me, senpai")

    words = request.GET.get('q', "").upper()
    words_author = request.GET.get('q_author', "").upper()
    words_series = request.GET.get('q_series', "").upper()
    words_title = request.GET.get('q_title', "").upper()
    book_code = request.GET.get('q_bookcode', "").upper()
    categories = request.GET.getlist('q_categories', [])
    states = request.GET.getlist('q_states', [])

    query = find_works(book_code, categories, states, words, words_author, words_series, words_title)

    query = query.filter(newseries__id__isnull=True)
    query = query.filter(subwork__id__isnull=True)

    query = query.order_by("book_code_sortable", "book_code_extension")
    query = query.distinct("book_code_sortable", "book_code_extension")
    return query


def find_works(book_code: str, categories: list[str], states: list[str], words: str,
               words_author: str, words_series: str, words_title: str) -> QuerySet[Work]:
    query = Work.objects

    query = query_annotate_bookcodes(query)
    any_query = False
    # If one word, also check bookcodes
    words_list = get_query_words(words)
    words_author_list = get_query_words(words_author)
    words_series_list = get_query_words(words_series)
    words_title_list = get_query_words(words_title)

    if len(words_list) == 1:
        any_query = True
        fbc = filter_book_code_get_q(words)
        fbt = filter_basic_text_get_q(words_list)
        quer = None
        for fb in fbt:
            if quer is None:
                quer = fb
            else:
                quer = Q(quer & fb)
        query = query.filter(fbc | quer)

    elif len(words_list) > 1:
        any_query = True
        query = filter_basic_text(query, words_list)

    if len(words_author_list) > 0:
        any_query = True
        query = filter_author_text(query, words_author_list)

    if len(words_series_list) > 0:
        any_query = True
        query = filter_series_text(query, words_series_list)

    if len(words_title_list) > 0:
        any_query = True
        query = filter_title_text(query, words_title_list)

    if len(categories) > 0:
        any_query = True
        query = filter_location(query, categories)

    if len(book_code) > 0:
        any_query = True
        query = query.filter(filter_book_code_get_q(book_code))

    if len(states) > 0:
        any_query = True
        query = filter_state(query, states)

    if not any_query:
        return Work.objects.none()


    return query


def query_annotate_bookcodes(query):
    query = query.annotate(
        itemid=F('item__id'),
        book_code_sortable=F('item__book_code_sortable'),
        book_code=F('item__book_code'),
        book_code_extension=F('item__book_code_extension')
    )

    return query