from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand

from book_code_generation.models import get_number_for_code
from creators.models import Creator, CreatorLocationNumber
from members.models import Committee
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS, WEB, KONNICHIWA, RETRIEVAL
from works.models import Item, Location


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        to_delete = []
        for cln in CreatorLocationNumber.objects.all():
            alias = cln.creator.is_alias_of
            if alias != cln.creator:
                cll = None
                try:
                    cll = CreatorLocationNumber.objects.get(creator=alias, location=cln.location)
                except CreatorLocationNumber.DoesNotExist:
                    continue
                if cll.number == cln.number and cll.letter == cln.letter:
                    to_delete.append(cln)
        for del_item in to_delete:
            del_item.delete()

