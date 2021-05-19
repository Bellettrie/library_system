from django.db import models

# Create your models here.

from creators.models import CreatorLocationNumber, LocationNumber

import re
import unicodedata

_ligature_re = re.compile(r'LATIN (?:(CAPITAL)|SMALL) LIGATURE ([A-Z]{2,})')


def split_ligatures(s):
    """
    Split the ligatures in `s` into their component letters.
    """

    def untie(letter):
        m = _ligature_re.match(unicodedata.name(letter))
        if not m:
            return letter
        elif m.group(1):
            return m.group(2)
        else:
            return m.group(2)

    return ''.join(untie(c) for c in s)


def normalize_str(strs):
    """Normalizes string in such a way that when sorted it's in the order we want. It destroys accents and merges IJ. Only works for western-like names"""
    strs = split_ligatures(strs).upper().replace("IJ", "Y").replace("ø".upper(), "O")
    data = strs
    normal = unicodedata.normalize('NFKD', data).encode('ASCII', 'ignore')
    return normal.decode('ASCII')


# Minimize number to a string: 370 --> 37.
def number_shrink_wrap(num):
    return str(float('0.' + str(num)))[2:]


# Get Z from code in SF-Z-34-lb1.
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


# Get 37 from SF-T-37-lr1
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


# Turn code with strange numbers into standardized numbers:
# SF-T-370-lr1 ==> SF-T-37-lr1
def standardize_code(cc: str):
    code = cc.replace(" ", "").replace(".","")
    code_parts = code.split("-")
    if len(code_parts) > 2:
        try:
            code_parts[2] = str(float("0." + code_parts[2])).split(".")[1]
        except ValueError:
            pass
    return_value = code_parts[0]
    for i in range(1, len(code_parts)):
        c = code_parts[i]
        if i == len(code_parts) - 1:
            num = 0
            c = ""
            for char in code_parts[i]:
                if char in "0123456789":
                    num *= 10
                    num += int(char)
                else:
                    if num > 0:
                        c += str.rjust(str(num), 6, "0")
                    c += char
        return_value = return_value + "-" + c
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

    def __str__(self):
        return self.name + "::" + str(self.number)


# Used to mock an item to run through the code, in case the item does not exist yet. Only contains the required fields for the item.
class FakeItem:
    def __init__(self, publication, location):
        self.publication = publication
        self.location = location
