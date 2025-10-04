import time

from django.core.management.base import BaseCommand

from search.models import WordMatch, SearchWord
from works.models import Publication


class Command(BaseCommand):
    help = 'Generate all search words for the current catalog.'

    def handle(self, *args, **options):
        words = None
        count = 0
        SearchWord.objects.all().delete()

        total = len(Publication.objects.all())
        start_time=time.time()
        for pub in Publication.objects.all():
            words = WordMatch.create_all_for(pub, words)
            count += 1
            if count % 100 == 0:
                print('Processed {}/{} in {}'.format(count, total, time.time()-start_time))
