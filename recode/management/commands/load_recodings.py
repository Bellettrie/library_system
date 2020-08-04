from random import random, randint

import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_USN, OLD_PWD
from lendings.models import Lending
from members.management.commands.namegen import generate_name, generate_full_name
from members.models import Member
from recode.models import Recode
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

        mycursor.execute("SELECT * FROM hercoderen")
        for x in mycursor:
            try:
                item = Item.objects.get(old_id=x.get("publicatienummer"))
                if len(Recode.objects.filter(item=item)) == 0:
                    Recode.objects.create(item=item, book_code=x.get("signatuur"), book_code_extension=x.get("exemplaar"))
            except Item.DoesNotExist:
                print(x.get("publicatienummer"))
