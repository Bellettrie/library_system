from django.core.management.base import BaseCommand
from django.db import transaction

from search.models import WordMatch, SearchWord
from works.models import Publication


class Command(BaseCommand):
    help = 'Generate all search words for the current catalog.'

    @transaction.atomic
    def handle(self, *args, **options):
        print("Started deleting")
        SearchWord.objects.all().delete()
        words = None
        print("finished deleting")
        for pub in Publication.objects.all():
            words = WordMatch.create_all_for(pub, words)
            print(pub.id)
        print("That's all folks")
