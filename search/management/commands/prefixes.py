from django.core.management.base import BaseCommand

from search.models import WordMatch, SearchWord
from works.models import Publication


def get_name(x):
    vn = x.get("voornaam")
    if len(vn) == 0:
        return x.get("naam")
    return vn + " " + x.get("naam")


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        words = dict()
        cc = 0

        for searchword in SearchWord.objects.all():
            z = ""
            for w in searchword.word:
                z += w
                words[z] = words.get(z, 0) + 1
                cc += 1
        print(len(words))
        print(cc / len(words))
