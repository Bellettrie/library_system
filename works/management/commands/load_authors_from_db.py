import datetime

import mysql.connector

from django.core.management.base import BaseCommand, CommandError

from series.models import Series, WorkInSeries, SeriesNode
from works.models import Work, WorkInPublication, Publication, SubWork, Creator


def get_name(x):
    vn = x.get("voornaam").decode("utf-8")
    if len(vn) == 0:
        return x.get("naam").decode("utf-8")
    return vn + " " + x.get("naam").decode("utf-8")


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    @staticmethod
    def handle_author(publication, tree, finder):
        data = finder.get(publication)

    @staticmethod
    def handle_matching(sub_work, tree, finder):
        data = finder.get(sub_work)

    def handle(self, *args, **options):
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="oldsystem"
        )
        mycursor = mydb.cursor(dictionary=True)

        persons = dict()

        mycursor.execute("SELECT * FROM persoon")

        count = 0
        for x in mycursor:
            persons[x.get("persoonnummer")] = x

        creators = dict()
        for p in persons.keys():
            old_id = persons.get(p).get("persoonnummer")
            comment = persons.get(p).get("commentaar")
            creator = Creator.objects.create(name=get_name(persons.get(p)), old_id=old_id, comment=comment)
            creators[old_id] = creator

        for p in persons.keys():
            connect_to = creators.get(persons.get(p).get("verwijzing"))
            if connect_to != 0:
                me = creators.get(persons.get(p).get("persoonnummer"))
                me.is_alias_of = connect_to
                me.save()
