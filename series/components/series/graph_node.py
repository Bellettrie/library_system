from typing import List

from works.models import Work, WorkRelation, CreatorToWork


class GraphNode:
    """
    The GraphNode represents a node in the tree-structure of a series. It concerns itself only with its own data, and its children.
    It is used by the tree renderer to walk over the tree.

    Normally, you don't want to use the constructor, since this would require quite some manual work. Instead, use the new_from_work method.ß
    """

    def __init__(self, work_relation: WorkRelation, path, creators=None):
        self.work_relation = work_relation
        self.path = path
        self.below = {}
        self.creators = creators or []

    def get_children(self):
        child_list = list(self.below.values())
        sorted_children = sorted(child_list, key=lambda x: x.work_relation.relation_index)
        return sorted_children

    def get_creators(self):
        return self.creators

    def get_work_relation(self):
        return self.work_relation

    @staticmethod
    def new_from_work(work: Work):
        """
        This creates a series_tree by starting at a specific work and moving both up and down over the relation.
        """
        graph_data = WorkRelation.RelationTraversal.series_down([work.id])
        graph_data = graph_data.prefetch_related(
            "from_work",
            "to_work",
            "from_work__item_set",
            "to_work__item_set")
        graph_data_up = WorkRelation.RelationTraversal.series_up([work.id])
        graph_data_up = graph_data_up.prefetch_related(
            "from_work",
            "to_work",
            "from_work__item_set",
            "to_work__item_set")

        graph_result = GraphNode.__upwards_graph_create(work, graph_data_up)

        for graph in graph_data:
            graph_result.__add_relation(graph)

        c2ws = GraphNode.__get_all_creators(work, list(graph_data_up) + list(graph_data))
        for c2w in c2ws:
            graph_result.__add_creator_to_work_to_subgraph(c2w)
        return graph_result

    @staticmethod
    def __upwards_graph_create(work, graph_data_up):
        graph_result = None
        for graph in graph_data_up:
            if graph_result is None:
                graph_result = GraphNode(graph, '_')
            else:
                graph_result = graph_result.__new_parent(graph)
        if graph_result is None:
            graph_result = GraphNode(WorkRelation(from_work=work, to_work=work), [work.id])
        else:
            graph_result = graph_result.__new_parent(
                WorkRelation(from_work=graph_data_up[-1].to_work, to_work=graph_data_up[-1].to_work))
        return graph_result

    @staticmethod
    def __get_all_creators(work, graph_data):
        works = [work]
        for rel in graph_data:
            works.append(rel.from_work)
            works.append(rel.to_work)

        c2ws = CreatorToWork.objects.filter(work__in=set(works)).select_related('creator')
        return c2ws

    def __new_parent(self, wr):
        gph = GraphNode(wr, '_')
        gph.below['_'] = self
        return gph

    def __add_creator_to_work_to_subgraph(self, creator_to_work: CreatorToWork):
        """
        The add_creator_to_work_to_subgraph method takes a creator_to_work relation, and:
        - if the work of the creator_to_work matches the work of the work_relation defined by this graph, then the creator is added to this graph-node
        - if it doesn't match, then it recursively tries adding it to the graphs below.
        """
        if self.work_relation.from_work_id == creator_to_work.work_id:
            # Prevent doubling in edge cases.
            if creator_to_work not in self.creators:
                self.creators.append(creator_to_work)
            return
        for x in self.below:
            self.below[x].__add_creator_to_work_to_subgraph(creator_to_work)

    def __add_relation(self, work_relation: WorkRelation):
        if work_relation.path is None:
            raise Exception("Tree building failed")

        if self.below.get('_') and len(self.below) == 1:
            self.below['_'].__add_relation(work_relation)
            return

        if len(work_relation.path) <= len(self.path):
            raise Exception("Tree building failed")

        bl = self.below.get(GraphNode.__path_to_string(work_relation.path))
        if bl is not None:
            return

        if len(work_relation.path) == len(self.path) + 1:
            pth = GraphNode.__path_to_string(work_relation.path)
            self.below[pth] = GraphNode(work_relation, work_relation.path)
            return

        lstlim = []
        for x in range(0, len(self.path) + 1):
            lstlim.append(work_relation.path[x])

        blz = GraphNode.__path_to_string(lstlim)
        bl = self.below.get(blz)

        if bl is not None:
            bl.__add_relation(work_relation)
            return

        raise Exception("Tree building failed")

    @staticmethod
    def __path_to_string(pth: List[int]):
        pt = list(map(str, pth))
        return ",".join(pt)
