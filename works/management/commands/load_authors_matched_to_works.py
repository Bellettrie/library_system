import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_PWD, OLD_USN
from series.models import Series, CreatorToSeries
from works.models import Work, Creator, CreatorRole, CreatorToWork


def get_name(x):
    vn = x.get("voornaam")
    if len(vn) == 0:
        return x.get("naam")
    return vn + " " + x.get("naam")


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        mydb = mysql.connector.connect(
            host="localhost",
            user=OLD_USN,
            passwd=OLD_PWD,
            database=OLD_DB
        )
        mycursor = mydb.cursor(dictionary=True)

        mycursor.execute("SELECT * FROM betrokkenheid")

        links = dict()
        list = []
        for x in mycursor:
            creator_role, updated = CreatorRole.objects.get_or_create(name=x.get("rol"))
            links[x.get("rol")] = creator_role
            list.append(x)

        for x in list:
            if len(Creator.objects.filter(old_id=x.get("persoonnummer"))) > 0:
                a = Creator.objects.get(old_id=x.get("persoonnummer"))
                if len(Work.objects.filter(old_id=x.get("publicatienummer"))) > 0:
                    w = Work.objects.get(old_id=x.get("publicatienummer"))
                    role = links.get(x.get("rol"))
                    CreatorToWork.objects.get_or_create(work=w, creator=a, role=role, number=x.get("lopend_nummer"))
                else:
                    if len(Series.objects.filter(old_id=x.get("publicatienummer"))) > 0:
                        w = Series.objects.get(old_id=x.get("publicatienummer"))

                        role = links.get(x.get("rol"))
                        CreatorToSeries.objects.get_or_create(series=w, creator=a, role=role, number=x.get("lopend_nummer"))
                    else:
                        print("Z" + str(x.get("publicatienummer")))
