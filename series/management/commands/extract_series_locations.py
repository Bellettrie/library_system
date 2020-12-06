from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand

from book_code_generation.models import get_number_for_code
from creators.models import Creator, CreatorLocationNumber
from members.models import Committee
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS, WEB, KONNICHIWA, \
    RETRIEVAL
from series.models import WorkInSeries, Series
from works.models import Item, Location, Publication


def get_publication_location(publication: Publication):
    item = Item.objects.filter(publication_id=publication.pk).first()
    if item:
        return item.location


class Command(BaseCommand):
    help = 'Set the locations of series, if all books are in the same location'

    def handle(self, *args, **options):
        series_dict = {}
        series_killed = set()
        act_set = set()
        for work_in_series in WorkInSeries.objects.all():
            data = series_dict.get(work_in_series.part_of_series)
            if data is None:
                data = get_publication_location(work_in_series.work)
            if data != get_publication_location(work_in_series.work):
                series_killed.add(work_in_series.part_of_series)
            series_dict[work_in_series.part_of_series] = data
            act_set.add(work_in_series.part_of_series)
        for series in series_dict.keys():
            if series not in series_killed:
                series.location = series_dict[series]
                series.save()

        blacklist = set()
        edited_something = True
        while edited_something:
            edited_something = False
            for series in Series.objects.all():
                pos = series.part_of_series
                if pos is not None and pos not in blacklist:
                    if pos.location is None:
                        edited_something = True
                        pos.location = series.location
                        pos.save()
                    else:
                        if pos.location != series.location:
                            edited_something = True
                            pos.location = None
                            pos.save()
                            blacklist.add(pos)
                            print(pos.get_canonical_title())
