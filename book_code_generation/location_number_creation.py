from book_code_generation.models import CodePin, normalize_str, CutterCodeRange
from creators.models import CreatorLocationNumber

from django.db.models import Q


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


# get the CodePins for a starting letter and a location, based on the fact that some authors should be ignored.
def get_authors_numbers(location, starting_letter, exclude_list=None):
    if exclude_list is None:
        exclude_list = []
    cutter_codes = CutterCodeRange.objects.order_by('from_affix').all()

    creator_codes = CreatorLocationNumber.objects.order_by('name').filter(
        ~Q(creator__in=exclude_list),
        letter=starting_letter,
        location=location
    )

    cutter_codes_idx = 0
    creator_codes_idx = 0
    result = [CodePin("", 1, "ZZZZZZZZZZZZ")]
    while True:
        # If we have read both lists entirely: break out of it
        if cutter_codes_idx == len(cutter_codes) and creator_codes_idx == len(creator_codes):
            break

        # If we are out of cutter codes, only look through the creator codes
        if cutter_codes_idx == len(cutter_codes):
            cc = creator_codes[creator_codes_idx]
            result[len(result) - 1].end = cc.name
            result.append(CodePin(cc.name, cc.number, "ZZZZZZZZZZZZ"))
            creator_codes_idx += 1
            continue

        # If we are out of creator codes, only look through the cutter codes
        if creator_codes_idx == len(creator_codes):
            cc = cutter_codes[cutter_codes_idx]
            result[len(result) - 1].end = cc.from_affix
            result.append(CodePin(cc.from_affix, cc.number, "ZZZZZZZZZZZZ"))
            cutter_codes_idx += 1

        # Both still have entries
        creator_code = creator_codes[creator_codes_idx]
        cutter_code = cutter_codes[cutter_codes_idx]

        # If they are the same, we only use the creator code.
        # We increment the cutter code as well, to skip it
        if creator_code.number == cutter_code.number:
            cc = creator_codes[creator_codes_idx]
            result[len(result) - 1].end = cc.name
            result.append(CodePin(cc.name, cc.number, "ZZZZZZZZZZZZ"))
            creator_codes_idx += 1
            cutter_codes_idx += 1
            continue

        # If the creator code number is larger than the cutter code number, add the cutter code number
        if creator_code.number > cutter_code.number:
            cc = cutter_codes[cutter_codes_idx]
            result[len(result) - 1].end = cc.from_affix
            result.append(CodePin(cc.from_affix, cc.number, "ZZZZZZZZZZZZ"))
            cutter_codes_idx += 1
        else:
            # if the cutter code number is larger than the creator code number, add the creator code
            cc = creator_codes[creator_codes_idx]
            result[len(result) - 1].end = cc.name
            result.append(CodePin(cc.name, cc.number, "ZZZZZZZZZZZZ"))
            creator_codes_idx += 1

    return result


# Get a new number for a certain name and location, with a list of ignored authors.
def get_new_number_for_location(location, name: str, exclude_list=[]):
    lst = get_authors_numbers(location, name[0], exclude_list)

    start = lst[0]
    end = start

    for codepin in lst:
        if codepin.name > normalize_str(name):
            end = codepin
            break
        start = codepin
    print(start.name, start.number, end.name, end.number)

    return get_numbers_between(start.number, end.number), start, end


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
def generate_author_number(name, location, exclude_list=[], include_one=False):
    if name is None or len(name) == 0:
        return None
    numbers, lower_bound, upper_bound = get_new_number_for_location(location, name, exclude_list)

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
