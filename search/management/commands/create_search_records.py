from django.core.management.base import BaseCommand

from creators.models import Creator
from members.models import Member
from search.models import WordMatch, SearchWord, SearchRecord
from series.models import Series, WorkInSeries
from works.models import Publication, SubWork, Item, CreatorToWork


class Command(BaseCommand):
    help = 'Generate all search records'

    def handle(self, *args, **options):
        SearchRecord.objects.all().delete()
        SearchRecord.search_record_for_publication(Publication.objects.first())

        creator_dict = dict()
        for creator in Creator.objects.all():
            creator_dict[creator.id] = creator

        for creator in Creator.objects.all():
            SearchRecord.search_record_for_author(creator, creator_dict)
        series_dict = dict()
        for series in Series.objects.prefetch_related("creatortoseries_set").all():
            series_dict[series.id] = series

        for series in series_dict.values():
            SearchRecord.search_record_for_series(series, series_dict, creator_dict)

        for publication in Publication.objects.all():
            SearchRecord.search_record_for_publication(publication)

        for member in Member.objects.all():
            SearchRecord.search_record_for_member(member)
