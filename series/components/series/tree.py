from django_components import Component, register

from series.components.series.graph_node import GraphNode
from works.models import Work


@register("series.Tree")
class Tree(Component):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_context_data(self, node: GraphNode, home_node: Work):
        return {
            'from_work': node.get_work_relation().from_work,
            'to_work': node.get_work_relation().to_work,
            'relation_index': node.get_work_relation().relation_index,
            'relation_index_label': node.get_work_relation().relation_index_label,
            'creators': node.get_creators(),
            'children': node.get_children(),
            'home_node': home_node,
        }

    template_name = "series/tree.html"
