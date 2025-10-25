from typing import List

from django.db import models
from django.db.models.query import RawQuerySet

from works.models import Work


class WorkRelation(models.Model):
    class RelationKind(models.IntegerChoices):
        sub_work_of = 1
        part_of_series = 2

    source_work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='outgoing_relations')
    target_work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='incoming_relations')

    relation_index = models.IntegerField()
    relation_index_label = models.CharField(max_length=64)

    relation_kind = models.IntegerField(choices=RelationKind.choices, db_index=True)

    class RelationTraversal:
        @staticmethod
        def for_search_words(work_id: int):
            up_types = [WorkRelation.RelationKind.part_of_series]
            down_types = [WorkRelation.RelationKind.sub_work_of]
            return WorkRelation.traverse_relations([work_id], up_types, down_types)

    @staticmethod
    def traverse_relations(work_ids: List[int], up_types: List[int], down_types: List[int]) -> RawQuerySet:
        """
        Traverse the WorkRelation model as a graph, recursively finding related WorkRelation rows.

        Starts from the given work_ids and traverses WorkRelation edges. The up_types and down_types control allowed traversal directions: a relation is followed forward if its relation_type is in up_types and its work_id matches; it's followed backward if its relation_type is in down_types and its relates_to_id matches.

        Args:
             work_ids: list of IDs of the works to start traversal from.
             up_types: relation type IDs that allow traversal forward (match on source_work_id).
             down_types: relation type IDs that allow traversal backward (match on target_work_id).

        Returns:
            A RawQuerySet of WorkRelation objects (prefetched with 'work' and 'relates_to').
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
                         relation_index,
                         relation_index_label,
                         relation_kind,
                         target_work_id,
                         source_work_id,
                         depth
                            )
                        AS
                        (SELECT id,
                                relation_index,
                                relation_index_label,
                                relation_kind,
                                target_work_id,
                                source_work_id,
                                1
                         FROM works_workrelation
                         WHERE (source_work_id    = ANY(%s::int[]) AND relation_kind IN (select * from up_types))
                            OR (target_work_id = ANY(%s::int[]) AND relation_kind IN (select * from down_types))
                         UNION
                         SELECT DISTINCT on (w.id)-- We recursively traverse over the relations
                                                  w.id,
                                                  w.relation_index,
                                                  w.relation_index_label,
                                                  w.relation_kind,
                                                  w.target_work_id,
                                                  w.source_work_id,
                                                  c.depth + 1
                         FROM works_workrelation w
                                  INNER JOIN cte_workrelations c
                                             ON -- use both ends of the already-found WorkRelations to find new ones if they match with the directions we are looking.
                                                 (
                                                     (
                                                         c.source_work_id = w.source_work_id AND
                                                         w.relation_kind IN (select * from up_types)
                                                         )
                                                         OR
                                                     (
                                                         c.target_work_id = w.source_work_id and
                                                         w.relation_kind IN (select * from up_types)
                                                         )
                                                         OR
                                                     (
                                                         c.target_work_id = w.target_work_id AND
                                                         w.relation_kind IN (select * from down_types)
                                                         )
                                                         OR
                                                     (
                                                         c.source_work_id = w.target_work_id AND
                                                         w.relation_kind IN (select * from down_types)
                                                         )
                                                     )
                        ) CYCLE id SET is_cycle USING path_cycle -- This prevents us from crashing the database if loops exist ;).
                SELECT distinct on (id) id,
                                        relation_index,
                                        relation_index_label,
                                        relation_kind,
                                        target_work_id,
                                        source_work_id,
                                        depth,
                                        path_cycle
                FROM cte_workrelations
                order by id, depth"""

        rel = WorkRelation.objects.raw(query, [up_types, down_types, work_ids, work_ids])
        rel = rel.prefetch_related('source_work', 'target_work')
        return rel

    def __str__(self):
        lvl = ""
        if hasattr(self, 'depth'):
            lvl = 'depth: ' + str(self.depth)

        if hasattr(self, 'path_cycle'):
            lvl += "cycle : " + str(self.path_cycle)
        return f'{self.source_work.title} -> {self.target_work.title}: {self.relation_index_label} -> {self.relation_kind} {lvl}'
