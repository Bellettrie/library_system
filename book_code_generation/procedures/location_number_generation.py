from book_code_generation.math import get_numbers_between, get_number_for_str
from book_code_generation.models import CutterCodeResult, CutterCodeRange
from book_code_generation.helpers import normalize_str, normalize_number
from creators.models import LocationNumber, CreatorLocationNumber


# Return a number for a name, location, exclude_list.
# Example: this generates something like 371 when generating for 'Tolkien', on location SF (so codes would become SF-T-371-...)
# Returns first letter of name, minimum number, recommended number, maximum number
def generate_location_number(name, location, exclude_list=None, exclude_location_list=None, include_one=False):
    if exclude_list is None:
        exclude_list = []
    if exclude_location_list is None:
        exclude_location_list = []
    if name is None or len(name) == 0:
        return None

    # We get the candidate numbers for the code generation, as well as the codes that will surround the new code.
    location_numbers = get_location_numbers(location, name[0], exclude_list, exclude_location_list)

    # We get the location_numbers just before and after the name
    start, end = get_location_number_bounds(location_numbers, name)

    # If the lower side is from the cutter table, we could replace that one with the new code.
    possible_results = get_numbers_between(start.number, end.number),

    if start.is_from_cutter_table:
        return name[0], start.number, start.number, possible_results[len(possible_results) - 1]

    result = get_recommended_result(name, start, end, possible_results, include_one)
    return name[0], possible_results[0], result, possible_results[len(possible_results) - 1]


def get_recommended_result(name, start, end, possible_results, include_one):
    # We calculate how far inbetween these two it should be (based on alphabetical distance).
    lower_num = get_number_for_str(start.name)
    upper_num = get_number_for_str(end.name)
    mid_num = get_number_for_str(normalize_str(name))
    if (upper_num - lower_num) == 0:
        diff = 0
    else:
        diff = (mid_num - lower_num) / (upper_num - lower_num)
    from math import floor
    num = floor(diff * len(possible_results))
    if not include_one and len(possible_results) > 1:
        num = max(1, num)
    result_id = max(0, min(len(possible_results) - 1, int(num)))
    return possible_results[result_id]


# For a list of cutter-numbers, returns which ones are just above and below the result.
def get_location_number_bounds(cutter_code_results, name: str):
    start = cutter_code_results[0]
    end = start

    for cutter_code_result in cutter_code_results:
        if cutter_code_result.name > normalize_str(name):
            end = cutter_code_result
            break
        start = cutter_code_result
    return start, end


# get the CodePins for a starting letter and a location, based on the fact that some authors should be ignored.
# This is based on a two-phase system:
# First we take the "standard cutter codes" as they are defined by our table (as per the code tables)
# Then we check which numbers are already given to authors & series in the same category, and what name belongs to those.
# For the author and series codes, we can tell the code to ignore some, because we want to be able to regenerate the same code for the same author/series.
# If there is overlap between the "standard cutter codes" and the "author/series codes", we remove the "standard cutter codes" where they overlap
def get_location_numbers(location, starting_letter, exclude_creator_list=None, exclude_locationnumber_in=None):
    if exclude_creator_list is None:
        exclude_creator_list = []
    if exclude_locationnumber_in is None:
        exclude_locationnumber_in = []

    codes = CutterCodeRange.objects.all()
    lst = []
    for code in codes:
        if code.from_affix.startswith(starting_letter):
            # Add a result to the list; store make it replaceable by the new code if-and-only-if it's not the first one.
            not_first_element = len(lst) > 0
            lst.append(
                CutterCodeResult(normalize_str(code.from_affix), normalize_number(code.number),
                                 normalize_str(code.to_affix), not_first_element))

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
            if normalize_number(letter.number) == code.number:
                if letter.number not in keys_done and code.name < l_name < code.end:
                    keys_done.add(letter.number)
                    to_hit = False
                    code.name = l_name
        if to_hit:
            my_letters.add(letter)
    for item in my_letters:
        l_name = normalize_str(item.name)

        if item.number not in letters:
            lst.append(CutterCodeResult(l_name, normalize_number(item.number)))

    # find the letter and number for an item / author / series, based on name and location.
    def get_key(obj):
        return obj.number

    lst.sort(key=get_key)
    lst.append(CutterCodeResult(starting_letter + "ZZZZZZZZZZZZ", 99999))
    return lst
