import datetime

import mysql.connector

from django.core.management.base import BaseCommand, CommandError

from bellettrie_library_system.settings import OLD_DB
from members.models import Member, Committee
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN
from series.models import Series, WorkInSeries, SeriesNode
from works.models import Work, WorkInPublication, Publication, SubWork, Creator


def get_name(x):
    vn = x.get("voornaam")
    if len(vn) == 0:
        return x.get("naam")
    return vn + " " + x.get("naam")


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'


    def handle(self, *args, **options):
        committees = [(KASCO, "Kascommittee", True),
                      (BOARD, "Board", True),
                      (ADMIN, "Administrators", True),
                      (COMCO, "Computer Committee", True),
                      (BOOKBUYERS, "Book Buyers", True),
                      (KICKIN, "Kickin Committee", True),
                      ]

        for committee in committees:
            if len(Committee.objects.filter(code=committee[0])) == 0:
                Committee.objects.create(name=committee[1], code=committee[0], active_member_committee=committee[2])
                print("added " + committee[1])
