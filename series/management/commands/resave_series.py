from django.core.management.base import BaseCommand
from django.db import transaction
from series.models import SeriesV2


class Command(BaseCommand):
    help = 'Resave series.'

    @transaction.atomic
    def handle(self, *args, **options):
        for sr in SeriesV2.objects.all():
            sr.save()
