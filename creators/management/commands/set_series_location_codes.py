from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand

from book_code_generation.models import get_number_for_code, get_letter_for_code
from creators.models import Creator, CreatorLocationNumber
from members.models import Committee
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS, WEB, KONNICHIWA, RETRIEVAL
from series.models import Series
from works.models import Item


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        for series in Series.objects.filter(part_of_series__isnull=True):
            auths = series.get_authors()
            if len(auths) > 0:
                author = auths[0].creator
                clns = CreatorLocationNumber.objects.filter(creator=author, location=series.location)
                if len(clns) == 1:
                    print(clns)
