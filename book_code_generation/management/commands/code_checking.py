from random import random, randint

import mysql.connector

from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_USN, OLD_PWD
from book_code_generation.models import CutterCodeRange, generate_code_from_author, generate_code_from_author_translated, generate_code_from_title, CodePin
from creators.models import CreatorLocationNumber
from members.management.commands.namegen import generate_name, generate_full_name
from members.models import Member
from works.models import Item, Creator, Location, Publication


# noinspection DuplicatedCode
def get_key(obj):
    return obj.name


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        from works.models import Location
        for location in Location.objects.all():
            n = location.category.name
            # for l in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            l='A'
            print(location)
            codes = CutterCodeRange.objects.all()
            lst = []
            for code in codes:
                if code.from_affix.startswith(l):
                    lst.append(CodePin(code.from_affix.upper(), int(code.number.strip("0"))))

            letters = list(CreatorLocationNumber.objects.filter(location=location, letter=l))
            for item in letters:
                    lst.append(CodePin(item.creator.name.upper() + " " + item.creator.given_names.upper(), item.number))
            lst.sort(key=get_key)
            prev = None
            num = 0
            for item in lst:
                if str(num) > str(item.number):
                    if prev:
                        print(item.name, item.number, num, prev)
                    else:
                        print(item.name, item.number, num)
                num = item.number
                prev = item.name