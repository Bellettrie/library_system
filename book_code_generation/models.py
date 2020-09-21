import unidecode as unidecode
from django.db import models

# Create your models here.

import re
import unicodedata

from creators.models import CreatorLocationNumber


def get_number_for_code(code: str):
    code_parts = code.split("-")
    if len(code_parts) > 2:
        try:
            return int(str(float("0." + code_parts[2])).split(".")[1])
        except ValueError:
            try:
                return int(str(float("0." + code_parts[1])).split(".")[1])
            except ValueError:
                if "ABC" not in code_parts:
                    print("ERROR" + code)
                pass


def standardize_code(code: str):
    code_parts = code.split("-")
    if len(code_parts) > 2:
        try:
            code_parts[2] = str(float("0." + code_parts[2])).split(".")[1]
        except ValueError:
            pass
    return_value = code_parts[0]
    for i in range(1, len(code_parts)):
        return_value = return_value + "-" + code_parts[i]
    return return_value


class BookCode(models.Model):
    class Meta:
        abstract = True

    book_code = models.CharField(max_length=64, blank=True)
    book_code_sortable = models.CharField(max_length=128, blank=True)

    def save(self, *args, **kwargs):
        self.book_code_sortable = standardize_code(self.book_code)
        super().save(*args, **kwargs)


class CodePin:
    def __init__(self, name: str, number: int):
        self.name = name
        self.number = number

    def __str__(self):
        return self.name + "::" + str(self.number)


def get_key(obj: CodePin):
    return obj.number


MAGIC_NUMBERS = [1, 2, 3, 4, 5, 6, 7, 8, 9]


def get_numbers_between(start, end):
    start_float = float("0." + str(start))
    end_float = float("0." + str(end))
    runs = 0
    numbers = []

    while (int(start_float) == int(end_float) or len(numbers) == 0) and runs <= 3:
        runs += 1
        start_float *= 10
        end_float *= 10
        start_int = int(start_float)
        runner = start_int
        while runner < end_float:
            for number in MAGIC_NUMBERS:
                target = runner * 10 + number
                if round(start_float * 1000) / 100 < target < round(end_float * 1000) / 100:
                    numbers.append(target)
            runner += 1
        if len(numbers) > 0:
            return numbers
    return [start]


def get_new_number_for_location(location, name: str, exclude_list=[]):
    from works.models import Location

    codes = CutterCodeRange.objects.all()
    lst = []
    for code in codes:
        if code.from_affix.startswith(name[0]):
            lst.append(CodePin(code.from_affix.upper(), int(code.number)))

    letters = list(CreatorLocationNumber.objects.filter(location=location, letter=name[0]))
    keys_done = set()
    my_letters = set()
    for letter in letters:
        if letter.creator in exclude_list:
            pass
        else:
            my_letters.add(letter)
            for code in lst:

                if letter.number == code.number:

                    if not letter.number in keys_done:
                        keys_done.add(letter.number)
                        code.name = letter.creator.name.upper() + " " + letter.creator.given_names.upper()
    for item in my_letters:
        if item.number not in letters:
            lst.append(CodePin(item.creator.name.upper() + " " + item.creator.given_names.upper(), item.number))
    lst.sort(key=get_key)
    lst.append(CodePin(name[0] + "ZZZZZZZZZZZZ", 99999))

    start = lst[0]
    end = start

    for codepin in lst:
        if codepin.name > name.upper():
            end = codepin
            break
        start = codepin
    return get_numbers_between(start.number, end.number), start, end


def strip_accents(text):
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """

    return unidecode.unidecode(text)


class CutterCodeRange(models.Model):
    from_affix = models.CharField(max_length=16)
    to_affix = models.CharField(max_length=16)
    number = models.CharField(max_length=16)
    generated_affix = models.CharField(max_length=20)

    @staticmethod
    def get_cutter_number(name: str):
        cutters = CutterCodeRange.objects.all().order_by("from_affix")
        result = None
        for cutter in cutters:
            if result is None:
                result = cutter
            if strip_accents(name.upper()) < cutter.from_affix:
                return result
            result = cutter
        return result


def get_key(creatorlocationnumber: CreatorLocationNumber):
    return str(creatorlocationnumber.number)


def get_number_for_str(string: str):
    number = 0
    for letter in string[::-1]:
        number = number / 10
        num = ord(letter) - 64
        if num > 26 or num < 1:
            num = 0
        num /= 2.6
        number += num
    return number


def generate_author_number(name, location, exclude_list=[]):
    if name is None or len(name) == 0:
        return None
    numbers, lower_bound, upper_bound = get_new_number_for_location(location, name, exclude_list)

    lower_num = get_number_for_str(lower_bound.name)
    upper_num = get_number_for_str(upper_bound.name)
    mid_num = get_number_for_str(name.upper())

    diff = (mid_num - lower_num) / (upper_num - lower_num)

    from math import floor
    num = floor(diff * len(numbers))
    if len(numbers) > 1:
        num = max(1, num)

    return numbers[max(0, min(len(numbers) - 1, num))]


def generate_code_from_author(item):
    pub = item.publication
    auth = pub.get_authors()
    if len(auth) > 0:
        author = auth[0].creator

        code = CutterCodeRange.get_cutter_number(author.name).generated_affix
        cl = CreatorLocationNumber.objects.filter(creator=author, location=item.location)

        if len(cl) == 1:
            code = author.name[0] + "-" + str(cl[0].number)
        else:
            if author.is_alias_of is not None and author.is_alias_of != author:
                my_author = author.is_alias_of
                cl = CreatorLocationNumber.objects.filter(creator=my_author, location=item.location)
                if len(cl) == 1:
                    code = my_author.name[0] + "-" + str(cl[0].number)
        return item.location.category.code + "-" + code + "-"
    else:
        pass


def generate_code_from_author_translated(item):
    pub = item.publication
    prefix = "N"
    if pub.is_translated:
        prefix = "V"
    auth = item.publication.get_authors()
    if len(auth) > 0:
        author = auth[0].creator

        code = CutterCodeRange.get_cutter_number(author.name).generated_affix
        cl = CreatorLocationNumber.objects.filter(creator=author, location=item.location)

        if len(cl) == 1:
            code = author.name[0] + "-" + str(cl[0].number)

        return prefix + "-" + code + "-"
    else:
        pass


def generate_code_abc(item):
    return item.location.category.code + "-ABC-"


def generate_code_from_title(item):
    title = item.publication.title[0:4]
    if item.location.category.code == "":
        return title + "-"
    else:
        return item.location.category.code + "-" + title + "-"


class FakeItem:
    def __init__(self, publication, location):
        self.publication = publication
        self.location = location
