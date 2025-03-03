import time

from django.contrib.postgres.search import TrigramWordSimilarity, TrigramStrictWordDistance
from django.core.management.base import BaseCommand
from django.db.models import Q, F


from search.models import  SearchRecord

import json


def show_explain(qs):
    plan = qs.explain(
        format="json",
        analyze=True,
        buffers=True,
        verbose=True,
        settings=True,
        wal=True,
    )
    print(json.dumps(plan))
    print(qs.explain( verbose=True))

def run_query(query, name):
    tm = time.time()

    print("\n \n ", name)
    print(query.query)
    show_explain(query)
    print("\n")
    print("results", len(query))
    print("time", time.time() - tm)
    for r in query[0:20]:
        if r.creator:
            print("CREATOR ", r.creator.get_name())
        elif r.member:
            print("MEMBER", r.member.name)
        else:
            print("PUB", r.publication.get_title(), r.publication.id)


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
    sim = None
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


class Command(BaseCommand):
    help = 'Generate all search records'

    def handle(self, *args, **options):
        run_query(ts_trigram_simple("dune"), "dune")
        run_query(ts_trigram_simple("hitch hiker"), "hitch hiker")
        run_query(ts_trigram_simple("it"), "it")
        run_query(ts_trigram_simple("king it"), "king it")
        run_query(ts_trigram_simple("stephen king it"), "king it")
        run_query(ts_trigram_simple("steven  king it"), "king it")
