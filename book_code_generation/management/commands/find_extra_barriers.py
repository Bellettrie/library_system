from random import random, randint

import mysql.connector

from django.core.management.base import BaseCommand

from book_code_generation.models import CodePin, normalize_str, number_shrink_wrap
from book_code_generation.location_number_creation import CutterCodeRange
from creators.models import CreatorLocationNumber, LocationNumber


# noinspection DuplicatedCode
def get_key(obj):
    return obj.name


class Command(BaseCommand):
    help = 'Displays out-of-order authors'

    def handle(self, *args, **options):
        print(normalize_str("Grøndahl, Jens Christian   (5289)"))
        from works.models import Location
        for location in Location.objects.all():
            for l in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                codes = CutterCodeRange.objects.all()
                lst = []
                for code in codes:
                    if code.from_affix.startswith(l):
                        lst.append(CodePin(normalize_str(code.from_affix), number_shrink_wrap(code.number)))

                letters = list(LocationNumber.objects.filter(location=location, letter=l))
                for item in letters:
                    lst.append(CodePin(normalize_str(item.name), item.number))
                lst.sort(key=get_key)
                prev = None
                num = 0
                for item in lst:
                    if str(num) > str(item.number):
                        if prev:
                            print(item.name, item.number, num, prev, location)
                        else:
                            print(item.name, item.number, num, location)
                    num = item.number
                    prev = item.name
