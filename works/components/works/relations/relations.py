from django.db.models import Q
from django.db.models.expressions import RawSQL, When, Case
from django_components import Component, register

from works.models import Item, Work, WorkRelation


@register("works.relations.Relations")
class Relations(Component):
    def get_context_data(self, work: Work):
        rels = WorkRelation.objects.filter(Q(from_work=work) | Q(to_work=work))
        rels = rels.annotate(iz=Case(When(from_work=work.id, then=0), default=1))
        rels = rels.order_by('relation_kind', "iz", 'relation_index')
        return {
            "relations": rels
        }

    template_name = "works/relations/relations.html"
