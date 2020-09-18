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
    lower_bound = CutterCodeRange.get_cutter_number(name)
    upper_bound = CutterCodeRange.objects.get(from_affix=lower_bound.to_affix)
    number = int(lower_bound.number)
    letters = list(CreatorLocationNumber.objects.filter(location=location, letter=name[0]))
    letters.sort(key=get_key)
    for letter in letters:
        print(letter.creator.name + letter.creator.given_names)
        if letter.creator in exclude_list:
            letters.remove(letter)
        pass
    old = lower_bound
    for letter in letters:
        print(letter.creator.name)
        lower_bound = old
        old = letter
        if (letter.creator.name+ " " + letter.creator.given_names).upper() > upper_bound.from_affix.upper():
            break
        if (letter.creator.name + " " + letter.creator.given_names).upper() > name.upper():
            upper_bound = letter
            break

    lower_bound_float = float(str('0.' + str(lower_bound.number)))
    lbn = lower_bound.number
    upper_bound_float = float(str('0.' + str(upper_bound.number)))
    ubn = upper_bound.number
    range = upper_bound_float - lower_bound_float

    if hasattr(lower_bound, 'from_affix'):
        lower_bound_name = lower_bound.from_affix
    else:
        lower_bound_name = lower_bound.creator.name + " " + lower_bound.creator.given_names
    lower_num = (get_number_for_str(lower_bound_name.upper()))
    if hasattr(upper_bound, 'to_affix'):
        upper_bound_name = upper_bound.to_affix
    else:
        upper_bound_name = upper_bound.creator.name + " " + upper_bound.creator.given_names
    upper_num = (get_number_for_str(upper_bound_name.upper()))
    mid_num = get_number_for_str(name.upper())

    diff = (mid_num - lower_num) / (upper_num - lower_num)
    print(lower_bound_name, name, upper_bound_name)


    my_len = 3
    num = str(lower_bound_float + diff * range)[2:5]

    while num == str(lbn)[:my_len] or num == str(ubn)[:my_len]:
        my_len += 1
        if my_len == 9:
            break
        num = str(lower_bound_float + diff * range)[2:2 + my_len]
    return int(num)


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
