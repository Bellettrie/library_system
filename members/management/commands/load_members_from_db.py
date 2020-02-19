import datetime

import mysql.connector

from django.core.management.base import BaseCommand, CommandError

from members.models import Member
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

        mycursor.execute("SELECT * FROM klant")

        count = 0
        for x in mycursor:
            z = Member.objects.filter(old_id=x.get("klantnummer"))
            if len(z) == 0:
                Member.objects.create(
                    name=x.get("voornaam").decode("utf-8") + " " + x.get("naam").decode("utf-8"),
                    nickname="",
                    addressLineOne=x.get("adres1").decode("utf-8"),
                    addressLineTwo=x.get("adres2").decode("utf-8"),
                    addressLineThree=x.get("adres3").decode("utf-8") + "\n" + x.get("adres4").decode("utf-8"),
                    email=x.get("email").decode("utf-8"),
                    phone=x.get("telefoon").decode("utf-8"),
                    student_number=x.get("unionpluskaartnummer"),
                    notes=x.get("opmerking"),
                    membership_type_old = x.get("herkomst"),
                    old_customer_type=x.get("lidsoort"),
                    old_id=x.get("klantnummer")
                )
