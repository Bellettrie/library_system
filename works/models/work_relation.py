from typing import List

from django.db import models
from django.db.models.query import RawQuerySet

from works.models import Work


class WorkRelation(models.Model):
    class RelationType(models.IntegerChoices):
        sub_work = 1
        series = 2

    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    relates_to = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='related_to')

    number_in_relation = models.IntegerField()
    display_number_in_relation = models.CharField(max_length=64)

    relation_type = models.IntegerField(choices=RelationType.choices)

    class RecursiveRelations:
        @staticmethod
        def search_words_relations(work_id: int):
            series_list = list(WorkRelation.recursive_work_relations_from([work_id], [WorkRelation.RelationType.series], []))
            subwork_list = list(WorkRelation.recursive_work_relations_from([work_id], [], [WorkRelation.RelationType.sub_work]))
            return series_list + subwork_list

    @staticmethod
    def recursive_work_relations_from(work_ids: List[int], up_types: List[int], down_types: List[int]) -> RawQuerySet:
        """
        This function is the main load-bearing function of the whole work relation setup.
        It starts from some specific work_ids and traverses the WorkRelations as a graph.
        The up_types and down_types define whether a work-relation can be added, either in forward or reverse direction.


        @param work_id: the ID of the work that we are trying to find the relations for
        @param up_types: the list of type_ids (as per RelationType). WorkRelations match if the work_id matches & up_type matches
        @param down_types: the list of type_ids (as per RelationType). WorkRelations match if the relates_to_id matches & down_type matches
        """
        # The main query is a bit of a monstrous recursive query.
        # Like any recursive query, it has an initial step (the first main select), and a recursive step (the select after the UNION).
        query = """
                WITH RECURSIVE
                up_types AS (SELECT unnest(%s::int[])),
                    down_types AS (SELECT unnest(%s::int[])),
                    cte_workrelations
                        (
                         id,
                         number_in_relation,
                         display_number_in_relation,
                         relation_type,
                         relates_to_id,
                         work_id,
                         depth
                            )
                        AS
                        (SELECT id,
                                number_in_relation,
                                display_number_in_relation,
                                relation_type,
                                relates_to_id,
                                work_id,
                                1
                         FROM works_workrelation
                         WHERE (work_id       = ANY(%s::int[]) AND relation_type IN (select * from up_types))
                            OR (relates_to_id = ANY(%s::int[]) AND relation_type IN (select * from down_types))
                         UNION
                         SELECT DISTINCT on (w.id)-- We recursively traverse over the relations
                                                  w.id,
                                                  w.number_in_relation,
                                                  w.display_number_in_relation,
                                                  w.relation_type,
                                                  w.relates_to_id,
                                                  w.work_id,
                                                  c.depth + 1
                         FROM works_workrelation w
                                  INNER JOIN cte_workrelations c
                                             ON -- use both ends of the already-found WorkRelations to find new ones if they match with the directions we are looking.
                                                 (
                                                     (
                                                         c.work_id = w.work_id AND
                                                         w.relation_type IN (select * from up_types)
                                                         )
                                                         OR
                                                     (
                                                         c.relates_to_id = w.work_id and
                                                         w.relation_type IN (select * from up_types)
                                                         )
                                                         OR
                                                     (
                                                         c.relates_to_id = w.relates_to_id AND
                                                         w.relation_type IN (select * from down_types)
                                                         )
                                                         OR
                                                     (
                                                         c.work_id = w.relates_to_id AND
                                                         w.relation_type IN (select * from down_types)
                                                         )
                                                     )
                        ) CYCLE id SET is_cycle USING path_cycle -- This prevents us from crashing the database if loops exist ;).
                SELECT distinct on (id) id,
                                        number_in_relation,
                                        display_number_in_relation,
                                        relation_type,
                                        relates_to_id,
                                        work_id,
                                        depth,
                                        path_cycle
                FROM cte_workrelations
                order by id, depth"""

        rel = WorkRelation.objects.raw(query, [up_types, down_types, work_ids, work_ids])
        rel = rel.prefetch_related('work', 'relates_to')
        return rel

    def __str__(self):
        lvl = ""
        if hasattr(self, 'depth'):
            lvl = 'depth: ' + str(self.depth)

        if hasattr(self, 'path_cycle'):
            lvl += "cycle : " + str(self.path_cycle)
        return f'{self.work.title} -> {self.relates_to.title}: {self.display_number_in_relation} -> {self.relation_type} {lvl}'
