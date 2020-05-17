from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB
from series.models import Series
from works.management.commands.load_works_from_db import fill_name
from works.models import Work


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    @staticmethod
    def handle_series_node(node, tree, finder):
        data = finder.get(node)
        series = Series.objects.get(old_id=node)
        fill_name(series, data)
        series.save()

    def handle(self, *args, **options):
        for work in Work.objects.all():
            work.update_listed_author()
