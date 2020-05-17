from django.core.management.base import BaseCommand

from works.models import Work


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        for work in Work.objects.all():
            work.update_listed_author()
