from django.core.management.base import BaseCommand

from datamining.views import get_member_statistics


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        get_member_statistics("2019-01-01")
