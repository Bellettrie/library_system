from random import random, randint

import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_USN, OLD_PWD
from book_code_generation.models import CutterCodeRange
from members.management.commands.namegen import generate_name, generate_full_name
from members.models import Member
from works.models import Item


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        from bellettrie_library_system.settings_migration import migration_database
        mycursor = migration_database.cursor(dictionary=True)

        mycursor.execute("SELECT * FROM cutter")
        CutterCodeRange.objects.all().delete()
        for x in mycursor:
            print(x)
            CutterCodeRange.objects.create(from_affix=x.get("begin").replace(" ", ""), to_affix=x.get("einde").replace(" ", ""), number=x.get("nummer"), generated_affix=x.get("combinatie").replace(" ", ""))
