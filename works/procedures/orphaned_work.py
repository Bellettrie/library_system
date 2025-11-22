from django.db.models import Q
from works.models import Work, WorkRelation, Item


def orphaned(work: Work):
    wrs = WorkRelation.objects.filter(Q(from_work=work) | Q(to_work=work))
    items = Item.objects.filter(publication=work)
    return len(wrs) == 0 and len(items) == 0
