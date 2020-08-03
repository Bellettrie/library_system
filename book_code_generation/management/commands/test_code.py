from random import random, randint

import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_USN, OLD_PWD
from book_code_generation.models import CutterCodeRange, generate_code_from_author, generate_code_from_author_translated, generate_code_from_title
from members.management.commands.namegen import generate_name, generate_full_name
from members.models import Member
from works.models import Item, Creator, Location


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        cutter = CutterCodeRange.get_cutter_number("Pratchett")
        print(cutter.generated_affix)
        items = Item.objects.filter(location=Location.objects.get(pk=3), publication__book_code__contains="-10-")

        for item in items:
            print(item)
            if not item.publication.book_code.startswith(item.generate_code_prefix()):
                print(item.publication.book_code, item.generate_code_prefix(), item.old_id)
