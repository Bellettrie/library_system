import datetime

import mysql.connector

from django.core.management.base import BaseCommand, CommandError

from bellettrie_library_system.settings import OLD_DB
from series.models import Series, WorkInSeries, SeriesNode
from works.models import Work, WorkInPublication, Publication, SubWork, Item, Category, ItemType


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

        ItemType.objects.get_or_create(name="Book", old_id=1)
        ItemType.objects.get_or_create(name="Comic", old_id=2)
        for x in mycursor:
            category = Category.objects.get_or_create(code=x.get("categorie"), name=x.get("locatienaam"), item_type=ItemType.objects.get(old_id=x.get("materiaalnummer")))

        mycursor.execute("SELECT * FROM band")

        for x in mycursor:
            z =  Item.objects.filter(old_id=x.get("publicatienummer"))
            for item in z:
                print(x.get("locatienummer"))
                if
                item.publication.category=Category.objects.get(old_id=x.get("locatienummer"))
                item.publication.save()

