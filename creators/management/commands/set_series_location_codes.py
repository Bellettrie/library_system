from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand

from book_code_generation.models import get_number_for_code, get_letter_for_code, number_shrink_wrap
from creators.models import Creator, CreatorLocationNumber, LocationNumber
from members.models import Committee
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS, WEB, KONNICHIWA, RETRIEVAL
from series.models import Series
from works.models import Item


def try_to_get_code_for(series: Series):
    book_letter = get_letter_for_code(series.book_code)
    book_nr = get_number_for_code(series.book_code)
    if book_letter and len(series.title) > 0 and book_letter.upper() == series.title[0].upper() and series.location is not None:
        print(series.title)
        if series.location_code is None:
            obj = LocationNumber.objects.create(name=series.title, location=series.location, letter=book_letter, number=book_nr)
            series.location_code = obj
            series.save()


class Command(BaseCommand):
    help = 'Set the location codes for series, if the series uses a different number from the creators number'

    def handle(self, *args, **options):
        for series in Series.objects.filter(part_of_series__isnull=True):
            auths = series.get_authors()
            if len(auths) > 0:
                author = auths[0].creator
                clns = CreatorLocationNumber.objects.filter(creator=author, location=series.location)
                if len(clns) == 1:
                    cln = clns[0]
                    if cln.letter != get_letter_for_code(series.book_code) or number_shrink_wrap(cln.number) != number_shrink_wrap(get_number_for_code(series.book_code)):
                        try_to_get_code_for(series)
                else:
                    print("ERROR")
            else:
                try_to_get_code_for(series)
