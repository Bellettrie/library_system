from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand

from book_code_generation.models import get_number_for_code, CutterCodeRange
from creators.models import Creator, CreatorLocationNumber
from members.models import Committee
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS, WEB, KONNICHIWA, RETRIEVAL
from works.models import Item, Location


def number_shrinking(num):
    return int(str(float("0." + num)).split(".")[1])


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        for creatornumber in CreatorLocationNumber.objects.filter():
            if creatornumber.creator.is_alias_of is not None and creatornumber.creator.is_alias_of is not creatornumber.creator:
                number = CutterCodeRange.get_cutter_number(creatornumber.creator.is_alias_of.name).number
                name = creatornumber.creator.is_alias_of.name

                if len(name) > 0 and name[0] == creatornumber.letter and number_shrinking(number) == creatornumber.number:
                    creatornumber.creator = creatornumber.creator.is_alias_of
                    print("bubbled for " + creatornumber.creator.get_name())
                    creatornumber.save()
