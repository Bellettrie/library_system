from typing import List

from creators.models import Creator


def get_all_author_aliases_by_ids(creator_ids: List[int]):
    query = """WITH RECURSIVE
                    ids AS (SELECT unnest(%s::int[])),
                        cte_creators
                            (
                             id,
                             given_names,
                             name,
                             is_alias_of_id,
                             comment,
                             old_id,
                             mark_for_change,
                             depth
                                )
                            AS
                            (SELECT  id,
                             given_names,
                             name,
                             is_alias_of_id,
                             comment,
                             old_id,
                             mark_for_change,
                             0
                             FROM creators_creator
                             WHERE id in (SELECT * FROM ids)
                             UNION
                             SELECT DISTINCT on (w.id)-- We recursively traverse over the relations
                                  w.id,
                                  w.given_names,
                                  w.name,
                                  w.is_alias_of_id,
                                  w.comment,
                                  w.old_id,
                                  w.mark_for_change,
                                  c.depth+1
                             FROM creators_creator w
                                INNER JOIN cte_creators c
                                 ON -- use both ends of the already-found WorkRelations to find new ones if they match with the directions we are looking.
                                     (
                                        w.id = c.is_alias_of_id
                                            OR
                                        w.is_alias_of_id = c.id
                                     )
                            ) CYCLE id SET is_cycle USING path_cycle -- This prevents us from crashing the database if loops exist ;).
                    SELECT distinct on (id) 
                        id,
                        given_names,
                        name,
                        is_alias_of_id,
                        comment,
                        old_id,
                        mark_for_change,
                        depth
                    FROM cte_creators
                    order by id"""

    return Creator.objects.raw(query, [creator_ids])