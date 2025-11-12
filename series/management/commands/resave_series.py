from django.core.management.base import BaseCommand
from django.db import transaction

from search.models import WordMatch, SearchWord
from series.models import SeriesV2
from works.models import Work


class Command(BaseCommand):
    help = 'Resave series.'

    @transaction.atomic
    def handle(self, *args, **options):
        for sr in SeriesV2.objects.all():
            sr.save()