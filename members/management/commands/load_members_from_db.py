import datetime

import mysql.connector

from django.core.management.base import BaseCommand, CommandError

from bellettrie_library_system.settings import OLD_DB
from members.models import Member
from series.models import Series, WorkInSeries, SeriesNode
from works.models import Work, WorkInPublication, Publication, SubWork, Creator


def get_name(x):
    vn = x.get("voornaam")
    if len(vn) == 0:
        return x.get("naam")
    return vn + " " + x.get("naam")


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
            database=OLD_DB
        )
        mycursor = mydb.cursor(dictionary=True)

        persons = dict()
        mycursor.execute("SELECT * FROM klant")

        count = 0
        for x in mycursor:
            z = Member.objects.filter(old_id=x.get("klantnummer"))
            if len(z) == 0:
                Member.objects.create(
                    name=x.get("voornaam") + " " + x.get("naam"),
                    nickname="",
                    addressLineOne=x.get("adres1"),
                    addressLineTwo=x.get("adres2"),
                    addressLineThree=x.get("adres3") + "\n" + x.get("adres4"),
                    email=x.get("email"),
                    phone=x.get("telefoon"),
                    student_number=x.get("unionpluskaartnummer"),
                    notes=x.get("opmerking"),
                    membership_type_old=x.get("herkomst"),
                    end_date=x.get("einde"),
                    old_customer_type=x.get("lidsoort"),
                    old_id=x.get("klantnummer")
                )

        if len(Member.objects.filter(is_anonymous_user=True)) == 0:
            Member.objects.create(
                name="Anonymous Monkey",
                nickname="",
                addressLineOne=" ",
                addressLineTwo=" ",
                addressLineThree=" ",
                email="board@bellettrie.utwente.nl",
                phone="- ---",
                student_number="- ---",
                notes="",
                membership_type_old="",
                end_date="2222-2-2",
                old_customer_type="admin",
                old_id=0,
                is_anonymous_user=True
            )
        else:
            print("Anonymous user was already there")
