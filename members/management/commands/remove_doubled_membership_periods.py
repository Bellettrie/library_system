from datetime import datetime, date

from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand
from members.models import Committee, Member, MembershipPeriod, MemberBackground, MembershipType


def mig():
    for member in Member.objects.all():
        member.try_and_delete_double_periods()


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        mig()
