import datetime

import mysql.connector

from django.core.management.base import BaseCommand, CommandError

from bellettrie_library_system.settings import OLD_DB
from series.models import Series, WorkInSeries, SeriesNode
from works.models import Work, WorkInPublication, Publication, SubWork, Item, Category, ItemType, Location


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database=OLD_DB
        )
        mycursor = mydb.cursor(dictionary=True)

        tree = dict()
        finder = dict()
        mycursor.execute("SELECT * FROM locatie where zichtbaar = 1")

        t1, new = ItemType.objects.get_or_create(name="Book", old_id=1)
        ItemType.objects.get_or_create(name="Comic", old_id=2)
        category, new = Category.objects.get_or_create(code="##", name="unknown", item_type=t1)
        Location.objects.get_or_create(category=category, old_id=0, name="")
        for x in mycursor:
            if x.get("materiaalnummer") <= 2:
                category, new = Category.objects.get_or_create(code=x.get("categorie"), name=x.get("locatienaam"),
                                                               item_type=ItemType.objects.get(
                                                                   old_id=x.get("materiaalnummer")))
                Location.objects.get_or_create(name=x.get("onderdeel"), category=category,
                                               old_id=x.get("locatienummer"))
        mycursor.execute("SELECT * FROM band")

        for x in mycursor:
            z = Item.objects.filter(old_id=x.get("publicatienummer"))
            for item in z:
                if x.get("locatienummer") == 0:
                    print(x)
                item.publication.location = Location.objects.get(old_id=x.get("locatienummer"))
                item.publication.save()
