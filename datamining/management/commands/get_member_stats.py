from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand

from book_code_generation.models import get_number_for_code, CutterCodeRange
from creators.models import Creator, CreatorLocationNumber
from datamining.views import get_member_statistics
from members.models import Committee
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS, WEB, KONNICHIWA, RETRIEVAL
from works.models import Item, Location


def number_shrinking(num):
    return int(str(float("0." + num)).split(".")[1])


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        get_member_statistics("2019-01-01")
