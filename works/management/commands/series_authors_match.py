import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_PWD, OLD_USN
from series.models import Series, CreatorToSeries
from works.models import Work, Creator, CreatorRole, CreatorToWork, Publication


def get_name(x):
    vn = x.get("voornaam")
    if len(vn) == 0:
        return x.get("naam")
    return vn + " " + x.get("naam")


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        for publication in Publication.objects.all():
            publication.update_listed_author()
