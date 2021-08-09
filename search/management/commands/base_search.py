from django.core.management.base import BaseCommand
from django.db.models import Q

from search.models import WordMatch, SearchWord, SeriesWordMatch
from search.queries import BaseSearchQuery, OrOp, AndOp, AuthorSearchQuery, SeriesSearchQuery, LocationSearchQuery
from series.models import Series
from works.models import Publication, Category
from works.views import get_works_for_publication


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        q = LocationSearchQuery(Category.objects.filter(name__contains="Fiction"))
        a = list(set(q.exec()))
        for z in a:
            print(z.get_title())
        print(len(a))
        s = Series.objects.filter(title__contains="Lord")[0]
        SeriesWordMatch.series_rename(s)
