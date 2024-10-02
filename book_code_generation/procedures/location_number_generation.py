from book_code_generation.math import get_numbers_between, get_number_for_str
from book_code_generation.models import CutterCodeResult, CutterCodeRange
from book_code_generation.helpers import normalize_str, normalize_number
from creators.models import LocationNumber, CreatorLocationNumber


# Return a number for a name, location, exclude_list.
# Example: this generates something like 371 when generating for 'Tolkien', on location SF (so codes would become SF-T-371-...)
# Returns first letter of name, minimum number, recommended number, maximum number
def generate_location_number(name, location, exclude_list=None, exclude_location_list=None, also_keep_first_result=False):
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
    possible_results = get_numbers_between(start.number, end.number)

    if start.is_from_cutter_table:
        return name[0], normalize_number(start.number), normalize_number(start.number), normalize_number(possible_results[len(possible_results) - 1])

    result = get_recommended_result(normalize_str(name), start.name, end.name, possible_results, also_keep_first_result)
    return name[0], normalize_number(possible_results[0]), normalize_number(result), normalize_number(possible_results[len(possible_results) - 1])


def get_recommended_result(name, start, end, possible_results, also_keep_first_result):
    # We calculate how far inbetween these two it should be (based on alphabetical distance).
    lower_num = get_number_for_str(start)
    upper_num = get_number_for_str(end)
    mid_num = get_number_for_str(name)

    if (upper_num - lower_num) == 0:
        diff = 0
    else:
        diff = (mid_num - lower_num) / (upper_num - lower_num)
    from math import floor
    num = floor(diff * len(possible_results))

    if not also_keep_first_result and len(possible_results) > 1:
        num = max(1, num)
    result_id = max(0, min(len(possible_results) - 1, int(num)))
    return possible_results[result_id]


# For a list of cutter-numbers, returns which ones are just above and below the result.
def get_location_number_bounds(cutter_code_results, name: str):
    start = cutter_code_results[0]
    for cutter_code_result in cutter_code_results:
        if cutter_code_result.name > normalize_str(name):
            return start, cutter_code_result
        start = cutter_code_result
    return start, start


# get the CodePins for a starting letter and a location, based on the fact that some authors should be ignored.
# This is based on a two-phase system:
# First we take the "standard cutter codes" as they are defined by our table (as per the code tables)
# Then we check which numbers are already given to authors & series in the same category, and what name belongs to those.
# For the author and series codes, we can tell the code to ignore some, because we want to be able to regenerate the same code for the same author/series.
# If there is overlap between the "standard cutter codes" and the "author/series codes", we remove the "standard cutter codes" where they overlap
def get_location_numbers(location, starting_letter, exclude_creator_list=None, exclude_locationnumber_id_in=None):
    if exclude_creator_list is None:
        exclude_creator_list = []
    if exclude_locationnumber_id_in is None:
        exclude_locationnumber_id_in = []


    # process the location aspecific codes
    codes = CutterCodeRange.objects.all().order_by('number')
    base_code_range = []
    for code in codes:
        if code.from_affix.startswith(starting_letter):
            # Add a result to the list; store make it replaceable by the new code if-and-only-if it's not the first one.
            not_first_element = len(base_code_range) > 0
            base_code_range.append(
                CutterCodeResult(normalize_str(code.from_affix), normalize_number(code.number),
                                 not_first_element))

    # Get the numbers for this location, with this letter, which are not excluded by the input variables
    location_numbers = list(LocationNumber.objects.filter(location=location, letter=starting_letter).exclude(
        pk__in=exclude_locationnumber_id_in).order_by('number'))

    # Exclude based on author (used for regenerating the number for an author that already has one)
    for c in CreatorLocationNumber.objects.filter(creator__in=exclude_creator_list):
        for my_loc in location_numbers:
            if my_loc.pk == c.pk:
                location_numbers.remove(my_loc)

    # First add the results based on the specific codes
    results = []
    for location_number in location_numbers:
        for code in base_code_range:
            # If there is overlap, we remove the base_code from the potential results
            if normalize_number(location_number.number) == code.number:
                base_code_range.remove(code)

        res = CutterCodeResult(normalize_str(location_number.name),
                               normalize_number(location_number.number),
                               False)
        results.append(res)

    # Add the base codes to the result
    for code in base_code_range:
        results.append(code)

    results.sort(key=lambda obj: obj.number)

    results.append(CutterCodeResult(starting_letter + "ZZZZZZZZZZZZ", 99999))
    return results
