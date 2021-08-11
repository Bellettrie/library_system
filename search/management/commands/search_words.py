from django.core.management.base import BaseCommand

from search.models import WordMatch, SearchWord
from works.models import Publication


class Command(BaseCommand):
    help = 'Generate all search words for the current catalog.'

    def handle(self, *args, **options):
        pubs = Publication.objects.all()
        SearchWord.objects.all().delete()
        words = None
        for pub in pubs:
            words = WordMatch.create_all_for(pub, words)
            print(pub.id)
