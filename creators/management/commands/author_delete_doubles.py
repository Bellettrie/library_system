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
        to_delete = []

        for cln in CreatorLocationNumber.objects.all():
            if cln in to_delete:
                continue
            for z in CreatorLocationNumber.objects.filter(creator=cln.creator, location=cln.location):
                if z != cln:
                    if z.letter != cln.letter or z.number != cln.number:
                        print(z.letter, z.number, cln.letter, cln.number, cln.creator, cln.location)
                    exp = CutterCodeRange.get_cutter_number(cln.creator.name.upper() +" "+cln.creator.given_names.upper())
                    if exp.number != cln.number or cln.letter != exp.from_affix[0]:
                        to_delete.append(cln)
                        break
                    else:
                        to_delete.append(z)
        for item in to_delete:
            item.delete()

