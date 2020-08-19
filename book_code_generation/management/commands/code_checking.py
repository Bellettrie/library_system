from random import random, randint

import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_USN, OLD_PWD
from book_code_generation.models import CutterCodeRange, generate_code_from_author, generate_code_from_author_translated, generate_code_from_title
from members.management.commands.namegen import generate_name, generate_full_name
from members.models import Member
from works.models import Item, Creator, Location, Publication


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):

        for pub in Publication.objects.all():
            pub.listed_author = pub.listed_author + "A"
            pub.save()
