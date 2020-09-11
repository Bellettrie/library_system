from django.core.management.base import BaseCommand

from recode.models import Recode
from series.models import WorkInSeries, SeriesNode
from works.models import Publication


def destroy_problems(*args, **options):
    ids = set()

    for r in Recode.objects.all():
        if r.item_id in ids:
            print(r)
        ids.add(r.item_id)
        print(r)


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        destroy_problems()
