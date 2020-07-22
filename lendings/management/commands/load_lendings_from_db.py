from random import random, randint

import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_USN, OLD_PWD
from lendings.models import Lending
from members.management.commands.namegen import generate_name, generate_full_name
from members.models import Member
from works.models import Item


def get_name(x):
    vn = x.get("voornaam")
    if len(vn) == 0:
        return x.get("naam")
    return vn + " " + x.get("naam")


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        from bellettrie_library_system.settings_migration import migration_database
        mycursor = migration_database.cursor(dictionary=True)

        mycursor.execute("SELECT * FROM uitlening")
        Lending.objects.all().delete()
        for x in mycursor:
            member = Member.objects.get(old_id=x.get("klantnummer"))
            if len(Item.objects.filter(old_id=x.get("publicatienummer"))) > 0:
                item = Item.objects.get(old_id=x.get("publicatienummer"))
                handed_in = x.get("ingenomen_op")
                handed_in_by = Member.objects.filter(old_id=x.get("ingenomen_door")).first()
                lended = x.get("uitgeleend_op")
                lended_by = Member.objects.filter(old_id=x.get("uitgeleend_door")).first()
                end_date = x.get("termijn")
                final_time = x.get("verlengd2_op") or x.get("verlengd1_op") or x.get("uitgeleend_op")
                # if handed_in is not None:
                #     continue
                times_extended = 0
                if x.get("verlengd2_op"):
                    times_extended += 1
                if x.get("verlengd1_op"):
                    times_extended += 1
                if lended is None:
                    continue
                Lending.objects.create(
                    member=member,
                    item=item,
                    lended_on=lended,
                    lended_by=lended_by,
                    times_extended=times_extended,
                    last_extended=final_time,
                    end_date=end_date,
                    handed_in=handed_in is not None,
                    handed_in_on=handed_in,
                    handed_in_by=handed_in_by)
