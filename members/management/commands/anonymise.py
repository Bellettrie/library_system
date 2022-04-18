import datetime

import mysql.connector

from django.core.management.base import BaseCommand

from members.models import Member
from members.procedures.anonymise import anonymise_or_except


def get_name(x):
    vn = x.get("voornaam")
    if len(vn) == 0:
        return x.get("naam")
    return vn + " " + x.get("naam")


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        counter = 0
        for member in Member.objects.all():

            if member.should_be_anonymised() and not member.is_blacklisted:
                # print(member)
                counter += 1
                print(member)
                should_delete = member.reunion_period_ended()
                anonymise_or_except(member, datetime.date.today(), dry_run=False)
                if should_delete and member.can_be_deleted():
                    member.delete()

        print(counter)
