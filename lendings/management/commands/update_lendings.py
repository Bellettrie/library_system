from django.core.management.base import BaseCommand

from lendings.procedures.get_end_date import get_end_date_for_lending
from lendings.models import Lending
from utils.time import get_now, get_today

class Command(BaseCommand):
    help = 'recalc lendings'

    def handle(self, *args, **options):
        for lending in Lending.objects.filter(handed_in=False):
            new_end = get_end_date_for_lending(lending, lending.last_extended or lending.start_date)
            if lending.end_date < new_end:
                lending.end_date = new_end
                lending.save()
