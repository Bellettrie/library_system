import unidecode as unidecode
from django.db import models

# Create your models here.

import re
import unicodedata

from django.db.models import CASCADE

from creators.models import CreatorLocationNumber


def turbo_str(strs):
    """ Normalise (normalize) unicode data in Python to remove umlauts, accents etc. """
    strs = strs.upper().replace("IJ", "Y")
    data = strs
    normal = unicodedata.normalize('NFKD', data).encode('ASCII', 'ignore')
    return normal.decode('ASCII')


def number_shrink_wrap(num):
    return str(float('0.' + str(num)))[2:]


def get_letter_for_code(code: str):
    code_parts = code.split("-")
    num = 0
    if len(code_parts) > 2:

        try:
            num = int(str(float("0." + code_parts[2])).split(".")[1])
            return code_parts[1]
        except ValueError:
            try:
                num = int(str(float("0." + code_parts[1])).split(".")[1])
                return None
            except ValueError:
                if "ABC" not in code_parts:
                    print("ERROR" + code)
                pass
    if num:
        return None


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
    def __init__(self, name: str, number: int, end='ZZZZZZZZZ', author=None):
        self.name = name
        self.number = number
        self.end = end
        self.author = author

    def __str__(self):
        return self.name + "::" + str(self.number)


def get_key(obj):
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


def get_authors_numbers(location, starting_letter, exclude_list=[]):
    from works.models import Location

    codes = CutterCodeRange.objects.all()
    lst = []
    for code in codes:
        if code.from_affix.startswith(starting_letter):
            lst.append(CodePin(turbo_str(code.from_affix), number_shrink_wrap(code.number), turbo_str(code.to_affix)))

    letters = list(CreatorLocationNumber.objects.filter(location=location, letter=starting_letter))
    keys_done = set()
    my_letters = set()
    for letter in letters:
        l_name = turbo_str(letter.creator.name + " " + letter.creator.given_names)
        to_hit = True
        for code in lst:
            if number_shrink_wrap(letter.number) == code.number:
                if letter.number not in keys_done and code.name < l_name < code.end:
                    keys_done.add(letter.number)
                    to_hit = False
                    code.name = l_name
                    code.author = letter.creator
        if to_hit:
            my_letters.add(letter)
    for item in my_letters:
        l_name = turbo_str(item.creator.name + " " + item.creator.given_names)

        if item.number not in letters:
            lst.append(CodePin(l_name, number_shrink_wrap(item.number), author=item.creator))
    lst.sort(key=get_key)
    lst.append(CodePin(starting_letter + "ZZZZZZZZZZZZ", 99999))
    return lst


def get_new_number_for_location(location, name: str, exclude_list=[]):
    lst = get_authors_numbers(location, name[0], exclude_list)

    start = lst[0]
    end = start

    for codepin in lst:
        if codepin.name > turbo_str(name):
            end = codepin
            break
        start = codepin
    print(start.name, start.number, end.name, end.number)

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
    location=models.ForeignKey("works.Location", default=None, null=True, blank=True, on_delete=CASCADE)
    @staticmethod
    def get_cutter_number(name: str, location = None):
        cutters = CutterCodeRange.objects.all().order_by("from_affix")

        result = None
        for cutter in cutters:
            if cutter.location is not None and cutter.location == location:
                continue
            if result is None:
                result = cutter
            if turbo_str(name) < cutter.from_affix:
                return result
            result = cutter
        return result


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


def generate_author_number(name, location, exclude_list=[], include_one=False):
    if name is None or len(name) == 0:
        return None
    numbers, lower_bound, upper_bound = get_new_number_for_location(location, name, exclude_list)

    lower_num = get_number_for_str(lower_bound.name)
    upper_num = get_number_for_str(upper_bound.name)
    mid_num = get_number_for_str(turbo_str(name))
    if (upper_num - lower_num) == 0:
        diff = 0
    else:
        diff = (mid_num - lower_num) / (upper_num - lower_num)

    from math import floor
    num = floor(diff * len(numbers))
    if not include_one and len(numbers) > 1:
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
