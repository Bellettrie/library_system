from django.core.management.base import BaseCommand
from works.models import Publication


def get_name(x):
    vn = x.get("voornaam")
    if len(vn) == 0:
        return x.get("naam")
    return vn + " " + x.get("naam")


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        pubs = Publication.objects.all()
        print(len(pubs))
        for pub in pubs:
            print(len(pub.item_set.all()))
            if len(pub.item_set.all()) > 0:
                print(pub.title)
                for item in pub.item_set:
                    print(item)
