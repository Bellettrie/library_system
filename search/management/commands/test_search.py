import time

from django.contrib.postgres.search import TrigramWordSimilarity, TrigramStrictWordDistance
from django.core.management.base import BaseCommand
from django.db.models import Q, F
from django.db.models.expressions import RawSQL

from search.models import  SearchRecord

def show_explain(qs):
    plan = qs.explain(
        format="json",
        analyze=True,
        buffers=True,
        verbose=True,
        settings=True,
        wal=True,
    )
    print(qs.explain( verbose=True))

def run_query(query, name):
    tm = time.time()

    print("\n \n ", name)
    print(query.query)
    show_explain(query)
    print("\n")
    print("results", len(query))
    print("time", time.time() - tm)
    for r in query[0:100]:
        if r.creator:
            print("CREATOR ", r.creator.get_name(), r.rank)
        elif r.member:
            print("MEMBER", r.member.name, r.rank)
        elif r.series:
            print("SERIES", r.series.get_title(), r.series.id, r.rank)
        else:
            print("PUB", r.item.publication.get_title(), r.item.publication.id, r.rank)


""" get_contains_query builds a search query based on the 'contains' operation."""
def get_contains_query(txt):
    q = None
    for word in txt.split(" "):
        qq = Q(all_text__contains=word)
        if q is None:
            q = qq
    return SearchRecord.objects.filter(q).extra(
        {'has_creator': 'creator_id is not NULL'}
    ).order_by('-has_creator')


def ts_trigram_similarity_query(txt):
    return SearchRecord.objects.annotate(
        similarity=TrigramStrictWordDistance(txt, "all_text"),
        similarityOrder=TrigramWordSimilarity(txt, "all_text")* F('result_priority'),
    ).filter(
        similarity__lt=0.3).order_by('-similarityOrder')

""" get_contains_query builds a search query based on trigram similarity"""
def ts_trigram_simple(txt):
    q = None
    sim = F('similarity')
    for word in txt.split(" "):
        qq = Q(all_text__trigram_word_similar=word)
        if q is None:
            q = qq
        else:
            q &= qq
        if sim is None:
            sim = TrigramWordSimilarity(txt, "all_text")
        else:
            sim = sim * TrigramWordSimilarity(txt, "all_text")

    return SearchRecord.objects.annotate(similarityOrder=sim).filter(q).order_by('-similarityOrder', '-result_priority')


def ts_vector_search(txt):
    txt = txt.lower()
    return SearchRecord.objects.annotate(
        rank=RawSQL("ts_rank(all_text_search_vector, websearch_to_tsquery('simple', %s))", [txt]),
    ).extra(where=["websearch_to_tsquery('simple', %s) @@ all_text_search_vector"], params=[txt]).filter(hidden=False).order_by('-rank')


class Command(BaseCommand):
    help = 'Run some test scenarios for search'

    def handle(self, *args, **options):
        run_query(ts_vector_search("lord of the rings"), "lord of the rings")
        run_query(ts_vector_search("lord rings"), "lord  rings")
        run_query(ts_vector_search("lotr"), "lotr")


        run_query(ts_vector_search("lord"), "lord")
        run_query(ts_vector_search("rings"), " rings")
        run_query(ts_vector_search("dune"), " dune")
        run_query(ts_vector_search("hitchhiker"), " hitchhiker")
        run_query(ts_vector_search("so long and thanks for all the fish"), " so long and thanks for all the fish")
        run_query(ts_vector_search("hitch hiker"), " hitch hiker")
        run_query(ts_vector_search("hg2g"), " hg2g")
        run_query(ts_vector_search("tolkien"), " tolkien")
        run_query(ts_vector_search("king"), " king")
