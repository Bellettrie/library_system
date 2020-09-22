from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand

from book_code_generation.models import get_number_for_code, CutterCodeRange
from creators.models import Creator, CreatorLocationNumber
from members.models import Committee
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS, WEB, KONNICHIWA, RETRIEVAL
from works.models import Item, Location


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        creator_locations = set()
        unlabeled = set()
        for creatornumber in CreatorLocationNumber.objects.all():
            creator_locations.add((creatornumber.creator, creatornumber.location))
        for item in Item.objects.all():
            if item.location.sig_gen == "author":
                authors = item.publication.get_authors()
                if len(authors) > 0:
                    auth = authors[0].creator
                    break_through = False
                    while auth is not None:
                        if (auth, item.location) in creator_locations:
                            break_through = True
                            break
                        if auth.is_alias_of == auth:
                            break
                        auth = auth.is_alias_of
                        if auth is None:
                            break

                    if break_through:
                        continue
                    if (authors[0].creator, item.location) not in unlabeled:
                        print(authors[0].creator, item.location)
                        unlabeled.add((authors[0].creator, item.location))
