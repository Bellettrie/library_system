from datetime import datetime, date

from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand
from members.models import Committee, Member, MembershipPeriod, MemberBackground, MembershipType
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS, WEB, KONNICHIWA, RETRIEVAL
from django.db import connection


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        for p in MembershipPeriod.objects.filter(end_date__gte="2088-01-01"):
            p.end_date = None
            p.save()