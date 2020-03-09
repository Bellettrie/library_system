import datetime

import mysql.connector
from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand, CommandError

from bellettrie_library_system.settings import OLD_DB
from members.models import Member, Committee
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS
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
        for member in Member.objects.all():
            member.update_groups()