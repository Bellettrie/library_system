import datetime

import mysql.connector

from django.core.management.base import BaseCommand, CommandError

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
            database="oldsystem2"
        )

        ddict = dict()
        for s in SeriesNode.objects.all():
                if (s.part_of_series, s.number) in ddict.keys():
                    ddict[(s.part_of_series, s.number)].append(s)
                else:
                    ddict[(s.part_of_series, s.number)] = [s]

        for z in ddict.keys():

            if len(ddict[z]) > 1:
                if z[0] is not None:
                    print(z[0].old_id, z[0].title, z[1])
                    for row in ddict[z]:
                        print(" >>" , row.old_id, row.number, row.title)
