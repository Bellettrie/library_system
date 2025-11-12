from typing import List

from django.db import models

# Create your models here.
from django.db.models import PROTECT, CASCADE

from book_code_generation.models import BookCode
from creators.models import LocationNumber
from works.models import NamedTranslatableThing, Location, WorkRelation

class SeriesV2(BookCode):
    work = models.OneToOneField("works.Work", on_delete=CASCADE)

    location = models.ForeignKey(Location, on_delete=PROTECT, null=True, blank=True)
    location_code = models.ForeignKey(LocationNumber, on_delete=PROTECT, null=True, blank=True)

    def relation_index_label(self):
        wr = self.work.part_of_series()
        if wr:
            return wr.relation_index_label
        return None

    def relation_index(self):
        wr = self.work.part_of_series()
        if wr:
            return wr.relation_index
        return None


class Graph:
    def new_parent(self, wr):
        gph = Graph(wr, '_')
        gph.below['_'] = self
        return gph

    @staticmethod
    def new_from_work(work):
        pk = work.id
        graph_data = WorkRelation.RelationTraversal.series_down([pk])
        graph_data = graph_data.prefetch_related(
            "from_work",
            "to_work",
            "from_work__item_set",
            "to_work__item_set")
        graph_data_up = WorkRelation.RelationTraversal.series_up([pk])
        graph_data_up = graph_data_up.prefetch_related(
            "from_work",
            "to_work",
            "from_work__item_set",
            "to_work__item_set")
        works = [work]
        for rel in graph_data:
            works.append(rel.from_work)
            works.append(rel.to_work)

        for rel in graph_data_up:
            works.append(rel.from_work)
            works.append(rel.to_work)

        from works.models import CreatorToWork
        c2ws = CreatorToWork.objects.filter(work__in=set(works)).select_related('creator')

        grph = None
        for graph in graph_data_up:
            if grph is None:
                grph = Graph(graph, '_')
            else:
                grph = grph.new_parent(graph)
        if len(graph_data_up) == 0:
            grph = Graph(WorkRelation(from_work=work, to_work=work), [pk])
        else:
            grph = grph.new_parent(WorkRelation(from_work=graph_data_up[-1].to_work, to_work=graph_data_up[-1].to_work))
        for graph in graph_data:
            grph.add_relation(graph)

        for c2w in c2ws:
            grph.bubble_creator(c2w)
        return grph

    def __init__(self, wr, path, creators=None):
        self.wr = wr
        self.path = path
        self.below = {}
        self.creators = creators or []

    def bubble_creator(self, creator_to_work):
        if self.wr.from_work_id == creator_to_work.work_id:
            self.creators.append(creator_to_work)
        for x in self.below:
            self.below[x].bubble_creator(creator_to_work)

    def get_children(self):
        child_list = list(self.below.values())
        sorted_children = sorted(child_list, key=lambda x: x.wr.relation_index)
        return sorted_children

    @staticmethod
    def path_zplurp(pth: List[int]):
        pt = list(map(str, pth))
        return ",".join(pt)

    def add_relation(self, wr: WorkRelation):
        if not hasattr(wr, "path"):
            print("NO PATH")
            return
        if self.below.get('_') and len(self.below) == 1:
            self.below['_'].add_relation(wr)
            return

        if len(wr.path) <= len(self.path):
            print("ERR")
            return
        bl = self.below.get(Graph.path_zplurp(wr.path))
        if bl is not None:
            return
        if len(wr.path) == len(self.path) + 1:
            pth = Graph.path_zplurp(wr.path)
            self.below[pth] = Graph(wr, wr.path)
            return

        lstlim = []
        for x in range(0, len(self.path) + 1):
            lstlim.append(wr.path[x])
        blz = Graph.path_zplurp(lstlim)
        bl = self.below.get(blz)
        if bl is not None:
            bl.add_relation(wr)
            return
        print("ERR 4")
