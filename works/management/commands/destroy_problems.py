from django.core.management.base import BaseCommand

from series.models import WorkInSeries, SeriesNode
from works.models import Publication


def destroy_problems(self, *args, **options):
    ddict = dict()
    for s in SeriesNode.objects.all():
        if (s.part_of_series, s.number) in ddict.keys():
            ddict[(s.part_of_series, s.number)].append(s)
        else:
            ddict[(s.part_of_series, s.number)] = [s]

    for z in ddict.keys():
        if len(ddict[z]) > 1:
            for row in ddict[z]:
                row.number = None
                row.save()
def get_name(x):
    vn = x.get("voornaam")
    if len(vn) == 0:
        return x.get("naam")
    return vn + " " + x.get("naam")


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        destroy_problems()

