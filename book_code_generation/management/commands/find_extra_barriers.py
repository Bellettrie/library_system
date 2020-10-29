from random import random, randint

import mysql.connector

from django.core.management.base import BaseCommand

from book_code_generation.models import CutterCodeRange, CodePin, turbo_str, number_shrink_wrap
from creators.models import CreatorLocationNumber


# noinspection DuplicatedCode
def get_key(obj):
    return obj.name


class Command(BaseCommand):
    help = 'Displays out-of-order authors'

    def handle(self, *args, **options):
        from works.models import Location
        for location in Location.objects.all():
            for l in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                codes = CutterCodeRange.objects.all()
                lst = []
                for code in codes:
                    if code.from_affix.startswith(l):
                        lst.append(CodePin(turbo_str(code.from_affix), number_shrink_wrap(code.number)))

                letters = list(CreatorLocationNumber.objects.filter(location=location, letter=l))
                for item in letters:
                    lst.append(CodePin(turbo_str(item.creator.name + " " + item.creator.given_names), item.number))
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
