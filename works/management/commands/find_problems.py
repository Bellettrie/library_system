import datetime

import mysql.connector

from django.core.management.base import BaseCommand, CommandError

from series.models import Series, WorkInSeries, SeriesNode
from works.models import Work, WorkInPublication, Publication, SubWork, Creator, Location


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
        # mydb = mysql.connector.connect(
        #     host="localhost",
        #     user="root",
        #     passwd="root",
        #     database="oldsystem2"
        # )

        category_dict = dict()
        ddict = dict()
        z_dict = dict()
        for s in SeriesNode.objects.all():
                if (s.part_of_series, s.number) in ddict.keys():
                    ddict[(s.part_of_series, s.number)].append(s)
                else:
                    ddict[(s.part_of_series, s.number)] = [s]
                if not (s.part_of_series, s.number) in category_dict.keys():
                    works = WorkInSeries.objects.filter(pk=s.pk)
                    for work_entry in works:
                        category_dict[(s.part_of_series, s.number)] = Publication.objects.get(pk=work_entry.work.pk).location.category.name

        done_set = set()
        for y in category_dict.values():

            if y in done_set:
                continue
            done_set.add(y)
            print()
            print(y)
            print("---")

            for z in ddict.keys():
                if len(ddict[z]) > 1:
                    if category_dict.get(z, 'unknown') == y:
                        if z[0] is not None:
                            print(z[0].old_id, z[1],  z[0].title)
                            for row in ddict[z]:
                                print(">>", row.old_id,  z[0].display_number, row.title)
