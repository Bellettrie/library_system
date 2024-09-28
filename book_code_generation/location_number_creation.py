from django.db import models
from django.db.models import Q

from book_code_generation.models import CodePin, normalize_str, number_shrink_wrap
from creators.models import LocationNumber, CreatorLocationNumber


# find the letter and number for an item / author / series, based on name and location.
# This file contains quite some helper-functions. The main function is at the bottom.
# Sorting key
def get_key(obj):
    return obj.number


# Which numbers to consider as postfixes for a book-code?
MAGIC_NUMBERS = [1, 2, 3, 4, 5, 6, 7, 8, 9]


# What numbers are between two numbers:
# Ie. 37, 38 -> [371, 372, 373, 374, 375,376, 377, 378]
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


def float_conv(number: str):
    return float("0." + str(number))


def number_between(number: str, minimum: str, maximum: str):
    number_fl = float_conv(number)
    minimum_fl = float_conv(minimum)
    maximum_fl = float_conv(maximum)
    return minimum_fl <= number_fl <= maximum_fl


# get the CodePins for a starting letter and a location, based on the fact that some authors should be ignored.
def get_authors_numbers(location, starting_letter, exclude_creator_list=None, exclude_locationnumber_in=None):
    if exclude_creator_list is None:
        exclude_creator_list = []
    if exclude_locationnumber_in is None:
        exclude_locationnumber_in = []
    from works.models import Location

    codes = CutterCodeRange.objects.all()
    lst = []
    for code in codes:
        if code.from_affix.startswith(starting_letter):
            lst.append(
                CodePin(normalize_str(code.from_affix), number_shrink_wrap(code.number), normalize_str(code.to_affix)))

    letters = list(LocationNumber.objects.filter(location=location, letter=starting_letter).exclude(
        pk__in=exclude_locationnumber_in))
    keys_done = set()
    my_letters = set()

    for c in CreatorLocationNumber.objects.filter(creator__in=exclude_creator_list):
        for my_letter in letters:
            if my_letter.pk == c.pk:
                letters.remove(my_letter)

    for letter in letters:
        l_name = normalize_str(letter.name)
        to_hit = True
        for code in lst:
            if number_shrink_wrap(letter.number) == code.number:
                if letter.number not in keys_done and code.name < l_name < code.end:
                    keys_done.add(letter.number)
                    to_hit = False
                    code.name = l_name
        if to_hit:
            my_letters.add(letter)
    for item in my_letters:
        l_name = normalize_str(item.name)

        if item.number not in letters:
            lst.append(CodePin(l_name, number_shrink_wrap(item.number)))
    lst.sort(key=get_key)
    lst.append(CodePin(starting_letter + "ZZZZZZZZZZZZ", 99999))
    return lst


# Get a new number for a certain name and location, with a list of ignored authors.
def get_new_number_for_location(location, name: str, exclude_creator_list=None, exclude_location_list=None):
    if exclude_creator_list is None:
        exclude_creator_list = []
    if exclude_location_list is None:
        exclude_location_list = []
    lst = get_authors_numbers(location, name[0], exclude_creator_list, exclude_location_list)

    start = lst[0]
    end = start

    for codepin in lst:
        if codepin.name > normalize_str(name):
            end = codepin
            break
        start = codepin

    return get_numbers_between(start.number, end.number), start, end


class CutterCodeRange(models.Model):
    from_affix = models.CharField(max_length=16)
    to_affix = models.CharField(max_length=16)
    number = models.CharField(max_length=16)
    generated_affix = models.CharField(max_length=20)

    @staticmethod
    def get_cutter_number(name: str, location=None):
        cutters = CutterCodeRange.objects.all().order_by("from_affix")

        result = None
        for cutter in cutters:
            if result is None:
                result = cutter
            if normalize_str(name) < cutter.from_affix:
                return result
            result = cutter
        return result


# Turn string into a number. Used to figure out what percentage of the possible strings are between something.
# Example, if we have: A = 1,  C = 2, E = 3, then we know that C is halfway between A and E.
# This function allows this for arbitrary words.
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


# Return a number for a name, location, exclude_list
# Returns first letter of name, minimum number, recommended number, maximum number
def generate_author_number(name, location, exclude_list=None, exclude_location_list=None, include_one=False):
    if exclude_list is None:
        exclude_list = []
    if exclude_location_list is None:
        exclude_location_list = []
    if name is None or len(name) == 0:
        return None
    numbers, lower_bound, upper_bound = get_new_number_for_location(location, name, exclude_list, exclude_location_list)

    lower_num = get_number_for_str(lower_bound.name)
    upper_num = get_number_for_str(upper_bound.name)
    mid_num = get_number_for_str(normalize_str(name))
    if (upper_num - lower_num) == 0:
        diff = 0
    else:
        diff = (mid_num - lower_num) / (upper_num - lower_num)

    from math import floor
    num = floor(diff * len(numbers))
    if not include_one and len(numbers) > 1:
        num = max(1, num)
    return name[0], numbers[0], numbers[max(0, min(len(numbers) - 1, int(num)))], numbers[len(numbers) - 1]
