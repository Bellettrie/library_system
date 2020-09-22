from random import random, randint

import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_USN, OLD_PWD
from book_code_generation.models import CutterCodeRange, generate_code_from_author, \
    generate_code_from_author_translated, generate_code_from_title, get_new_number_for_location, get_numbers_between
from members.management.commands.namegen import generate_name, generate_full_name
from members.models import Member
from works.models import Item, Creator, Location, Publication


class Command(BaseCommand):
    help = 'Simple test of calculating numbers'

    def handle(self, *args, **options):
        print(get_new_number_for_location(None, 'Adams'))
        print(get_numbers_between(201, 212))
