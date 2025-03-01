import time

from django.contrib.postgres.search import TrigramWordSimilarity
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


def get_contains_query():
    return SearchRecord.objects.filter(Q(all_text__contains='dam'), Q(all_text__contains="kylian")).extra(
        {'has_creator': 'creator_id is not NULL'}
    ).order_by('-has_creator')


def ts_trigram_similarity_query(txt):
    return SearchRecord.objects.annotate(
        similarity=TrigramWordSimilarity(txt, "all_text"),
        similarityOrder=TrigramWordSimilarity(txt, "all_text")* F('result_priority'),
    ).filter(
        similarity__gt=0.6).order_by('-similarityOrder')


class Command(BaseCommand):
    help = 'Generate all search records'

    def handle(self, *args, **options):
        run_query(get_contains_query(), "contains query")
        run_query(ts_trigram_similarity_query("kylian dam"), "trigram similarity query frank herbert")

        run_query(ts_trigram_similarity_query("frank herbert"), "trigram similarity query frank herbert")
        run_query(ts_trigram_similarity_query("charlie"), "trigram similarity query charlie")
        run_query(ts_trigram_similarity_query("james"), "trigram similarity query james")
        run_query(ts_trigram_similarity_query("james barringt"), "trigram similarity query james barringt")
        run_query(ts_trigram_similarity_query("hitch adams"), "trigram similarity query hitch adams")
