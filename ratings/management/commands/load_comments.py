from random import random, randint

import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_USN, OLD_PWD
from lendings.models import Lending
from members.management.commands.namegen import generate_name, generate_full_name
from members.models import Member
from ratings.models import Rating, Comment
from works.models import Item, Publication


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

        mycursor.execute("SELECT * FROM commentaar")
        Comment.objects.all().delete()
        for x in mycursor:
            try:
                publication = Publication.objects.get(old_id=x.get("publicatienummer"))

                Comment.objects.create(publication=publication, comment=x.get("tekst"), author=x.get("auteur")[0:16], date=x.get("datum"), accepted=x.get("goedgekeurd"))
            except Publication.DoesNotExist:
                pass
            except Member.DoesNotExist:
                pass
