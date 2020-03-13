import datetime

import mysql.connector
from django.contrib.auth.models import Group, Permission

from django.core.management.base import BaseCommand, CommandError

from bellettrie_library_system.settings import OLD_DB
from members.models import Member, Committee
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS
from series.models import Series, WorkInSeries, SeriesNode
from works.models import Work, WorkInPublication, Publication, SubWork, Creator


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    @staticmethod
    def get_rights(committee):
        if committee == KASCO:
            return [""]
        if committee == LENDERS:
            return [] + all_rights("members", "member") + \
                   all_rights("lendings", "lending") + \
                   view_rights("works", "work") + \
                   view_rights("works", "series")

    def handle(self, *args, **options):
        committees = [(KASCO, "Kascommittee", True),
                      (BOARD, "Board", True),
                      (ADMIN, "Administrators", True),
                      (COMCO, "Computer Committee", True),
                      (BOOKS, "Books Committee", True),
                      (BOOKBUYERS, "Book Buyers", True),
                      (KICKIN, "Kickin Committee", True),
                      (LENDERS, "Lenders Committee", True),
                      ]

        for committee in committees:
            if len(Committee.objects.filter(code=committee[0])) == 0:
                Committee.objects.create(name=committee[1], code=committee[0], active_member_committee=committee[2])
                print("added " + committee[1])
            if len(Group.objects.filter(name=committee[0])) == 0:
                Group.objects.create(name=committee[0])
                print("added GROUP FOR " + committee[1])



