from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand

from book_code_generation.models import get_number_for_code
from creators.models import Creator, CreatorLocationNumber
from members.models import Committee
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS, WEB, KONNICHIWA, RETRIEVAL
from works.models import Item


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        CreatorLocationNumber.objects.all().delete()
        items = Item.objects.all()
        print("DONE1")
        item_to_author = dict()
        for item in items:
            authors = item.publication.get_authors()
            if len(authors) > 0:
                item_to_author[item] = authors[0].creator
            else:
                item_to_author[item] = None
        print("DONE2")
        for creator in Creator.objects.all():
            location_dict = dict()
            letter = ""
            if len(creator.name) > 0:
                letter = creator.name[0]
            for item in items:
                if item_to_author[item] == creator:
                    lz = location_dict.get(item.location, [])
                    lz.append(item)
                    location_dict[item.location] = lz

            for key in location_dict.keys():
                code_dict = dict()
                high_count = 0
                final_code = 0

                for item in location_dict[key]:
                    book_nr = get_number_for_code(item.book_code)
                    count = code_dict.get(book_nr, 0)
                    count += 1
                    high_count = max(count, high_count)
                    if count == high_count:
                        if book_nr is not None:
                            final_code = book_nr

                    code_dict[book_nr] = count
                if final_code > 0:
                    CreatorLocationNumber.objects.create(creator=creator, location=key, number=final_code, letter=letter)
