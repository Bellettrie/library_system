import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_PWD, OLD_USN
from series.models import Series, CreatorToSeries
from works.models import Work, Creator, CreatorRole, CreatorToWork, Item


def get_name(x):
    vn = x.get("voornaam")
    if len(vn) == 0:
        return x.get("naam")
    return vn + " " + x.get("naam")


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        from bellettrie_library_system.settings_migration import migration_database
        mycursor = migration_database.cursor(dictionary=True)

        mycursor.execute("SELECT * FROM band")

        links = dict()
        list = []
        for x in mycursor:
            try:
                item = Item.objects.get(old_id=x.get("publicatienummer"))
                item.publication_year = x.get("uitgavejaar")
                item.save()
            except Item.DoesNotExist:
                pass
