from typing import List

from django.db import models
from django.db.models.query import RawQuerySet

from works.models import Work


class WorkRelation(models.Model):
    """
    The WorkRelation model is used to represent the relations between Works in the system.

    """

    class RelationKind(models.IntegerChoices):
        sub_work_of = 1
        part_of_series = 2
        part_of_secondary_series = 3
        translation_of = 4

    from_work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='outgoing_relations')
    to_work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='incoming_relations')

    relation_index = models.DecimalField(null=True, blank=True, decimal_places=1, max_digits=5)
    relation_index_label = models.CharField(max_length=64)

    relation_kind = models.IntegerField(choices=RelationKind.choices, db_index=True)

    def relation_index_as_text(self):
        if float(int(self.relation_index)) == float(self.relation_index):
            return str(int(self.relation_index))
        return str(self.relation_index)

    class RelationTraversal:
        @staticmethod
        def for_search_words(work_ids: List[int]):
            up_types = [WorkRelation.RelationKind.part_of_series, WorkRelation.RelationKind.part_of_secondary_series]
            down_types = [WorkRelation.RelationKind.sub_work_of]
            return WorkRelation.traverse_relations(work_ids, up_types, down_types)

        @staticmethod
        def for_search_words_inverse(work_ids: List[int]):
            up_types = [WorkRelation.RelationKind.sub_work_of]
            down_types = [WorkRelation.RelationKind.part_of_series, WorkRelation.RelationKind.part_of_secondary_series]

            return WorkRelation.traverse_relations(work_ids, up_types, down_types)

    @staticmethod
    def traverse_relations(work_ids: List[int], forward_kinds: List[int], reverse_kinds: List[int],
                           further_away_first=False) -> RawQuerySet:
        """
        Traverse the WorkRelation model as a graph, recursively finding related WorkRelation rows.

        Starts from the given work_ids and traverses WorkRelation edges. The forward_kinds and reverse_kinds control allowed traversal directions: a relation is followed forward if its relation_type is in forward_kinds and its from_work_id matches; it's followed backward if its relation_type is in reverse_kinds and its to_work_id matches.

        Args:
             work_ids: list of IDs of the works to start traversal from.
             forward_kinds: relation type IDs that allow traversal forward (match on from_work_id).
             reverse_kinds: relation type IDs that allow traversal backward (match on to_work_id).

        Returns:
            A RawQuerySet of WorkRelation objects (prefetched with 'from_work' and 'to_work').
        """

        # The main query is a bit of a monstrous recursive query.
        # Like any recursive query, it has an initial step (the first main select), and a recursive step (the select after the UNION).
        query = """
                WITH RECURSIVE
                forward_kinds AS (SELECT unnest(%(forward_kinds)s::int[])),
                    reverse_kinds AS (SELECT unnest(%(reverse_kinds)s::int[])),
                    cte_workrelations
                        (
                         id,
                         relation_index,
                         relation_index_label,
                         relation_kind,
                         from_work_id,
                         to_work_id,
                         depth,
                         path,
                         fwd
                            )
                        AS
                        (SELECT id,
                                relation_index,
                                relation_index_label,
                                relation_kind,
                                from_work_id,
                                to_work_id,
                                1,
                                array[case when from_work_id = ANY(%(work_ids)s::int[]) then from_work_id else to_work_id end, %(mul)s * relation_index] as path,
                                from_work_id = ANY(%(work_ids)s::int[]) as fwd
                         FROM works_workrelation
                         WHERE (from_work_id    = ANY(%(work_ids)s::int[]) AND relation_kind IN (select * from forward_kinds))
                            OR (to_work_id = ANY(%(work_ids)s::int[]) AND relation_kind IN (select * from reverse_kinds))
                         UNION
                         SELECT DISTINCT on (w.id)-- We recursively traverse over the relations
                                                  w.id,
                                                  w.relation_index,
                                                  w.relation_index_label,
                                                  w.relation_kind,
                                                  w.from_work_id,
                                                  w.to_work_id,
                                                  c.depth + 1,
                                                  c.path || %(mul)s * w.relation_index,
                                                  ( c.from_work_id = w.from_work_id or c.to_work_id = w.from_work_id ) as fwd
                         FROM works_workrelation w
                                  INNER JOIN cte_workrelations c
                                             ON -- use both ends of the already-found WorkRelations to find new ones if they match with the directions we are looking.
                                                 (
                                                     (
                                                         c.id != w.id AND
                                                         c.from_work_id = w.from_work_id AND
                                                         w.relation_kind IN (select * from forward_kinds) AND
                                                         not c.fwd
                                                         )
                                                         OR
                                                     (
                                                         c.id != w.id AND
                                                         c.to_work_id = w.from_work_id and
                                                         w.relation_kind IN (select * from forward_kinds)
                                                         AND c.fwd
                                                         )
                                                         OR
                                                     (
                                                         c.id != w.id AND
                                                         c.to_work_id = w.to_work_id AND
                                                         w.relation_kind IN (select * from reverse_kinds)
                                                         AND c.fwd
                                                         )
                                                         OR
                                                     (
                                                         c.id != w.id AND
                                                         c.from_work_id = w.to_work_id AND
                                                         w.relation_kind IN (select * from reverse_kinds)
                                                         AND NOT c.fwd
                                                         )
                                                     )
                        ) CYCLE id SET is_cycle USING path_cycle -- This prevents us from crashing the database if loops exist ;).
                SELECT distinct on (path) id,
                                        relation_index,
                                        relation_index_label,
                                        relation_kind,
                                        from_work_id,
                                        to_work_id,
                                        path
                FROM cte_workrelations
                order by path"""

        query += " DESC" if further_away_first else " ASC"

        rel = WorkRelation.objects.raw(query, {"forward_kinds": forward_kinds, "reverse_kinds": reverse_kinds,
                                               "work_ids": work_ids, "mul": -1 if further_away_first else 1})
        rel = rel.prefetch_related('from_work', 'to_work')
        return rel

    def __str__(self):
        path = ""
        if hasattr(self, 'path'):
            path += "path : " + str(self.path)
        return f'{self.from_work.title} -> {self.to_work.title}: {self.relation_index_label} -> {self.relation_kind} {path}'
