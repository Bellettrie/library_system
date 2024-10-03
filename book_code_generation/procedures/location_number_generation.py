from typing import List, Tuple

from book_code_generation.models import CutterCodeResult, CutterCodeRange
from book_code_generation.helpers import normalize_str, normalize_number, get_numbers_between, get_number_for_str
from creators.models import LocationNumber, CreatorLocationNumber, Creator
from works.models import Location


def generate_location_number(name: str, location: Location, exclude_list: List[Creator] = None,
                             exclude_location_list: List[LocationNumber] = None,
                             also_keep_first_result: bool = False) -> Tuple[str, str, str, str]:
    """
    get_location_number returns the letter, lowest possible code number, recommended code number and highest possible code number for a name & location
    :param name: The name for which a number should be selected
    :param location: The location for which a number should be selected
    :param exclude_list: List of creators that should be excluded from generation
    :param exclude_location_list: List of creator_locations that should be excluded from generation
    :param also_keep_first_result: Whether to skip the first result
    :return: The starting letter of the name, lowest possible code number, recommended code number and highest possible code number for a name.
    """
    if exclude_list is None:
        exclude_list = []
    if exclude_location_list is None:
        exclude_location_list = []
    if name is None or len(name) == 0:
        return "Name cannot be empty", "", "", ""

    normalized_name = normalize_str(name)
    first_letter = normalized_name[0]

    # We get the candidate numbers for the code generation, as well as the codes that will surround the new code.
    location_numbers = get_location_numbers(location, first_letter, exclude_list, exclude_location_list)

    # We get the location_numbers just before and after the name
    start, end = get_location_number_bounds(location_numbers, normalized_name)

    possible_results = get_numbers_between(start.number, end.number)

    lowest_result = normalize_number(possible_results[0])
    highest_result = normalize_number(possible_results[len(possible_results) - 1])

    # If the lower side is from the cutter table, we could replace that one with the new code.
    if start.is_from_cutter_table:
        lowest_result = normalize_number(start.number)
        recommended_result = lowest_result
    else:
        recommended_result = normalize_number(
            get_recommended_result(normalized_name, start.name, end.name, possible_results,
                                   also_keep_first_result))

    return first_letter, lowest_result, recommended_result, highest_result


def get_recommended_result(name: str, start: str, end: str, possible_results: List[str],
                           also_keep_first_result: bool = False) -> str:
    """ get_recommended_result gives a single recommended location number for a name, based on the names of the locations just before/after, and a list of candidate numbers.
    :param name The name for which a number is selected
    :param start The name belonging to the number just before it
    :param end The name belonging to the number after it
    :param possible_results The list of candidate numbers
    :param also_keep_first_result If True, it will not skip the first element in possible_results
    """
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


def get_location_number_bounds(cutter_code_results: List[CutterCodeResult], name: str) \
        -> Tuple[
            CutterCodeResult, CutterCodeResult
        ]:
    """
    get_location_number_bounds gives the cutter-numbers just above and below the name
    :param cutter_code_results: A list of cutter_code_results
    :param name:  The name for which to look for the ones just above/below.
    :return:
    """
    start = cutter_code_results[0]
    for cutter_code_result in cutter_code_results:
        if cutter_code_result.name > name:
            return start, cutter_code_result
        start = cutter_code_result
    return start, start


def get_location_numbers(location: Location,
                         starting_letter: str,
                         exclude_creator_list: List[Creator] = None,
                         exclude_locationnumber_id_in: List[LocationNumber] = None) -> List[CutterCodeResult]:
    """
    get_location_numbers returns the CutterCodeRanges for a starting letter and a location, based on the fact that some authors should be ignored.
    This is based on a two-phase system:
    First we take the "standard cutter codes" as they are defined by our table (as per the code tables)
    Then we check which numbers are already given to authors & series in the same category, and what name belongs to those.
    For the author and series codes, we can tell the code to ignore some, because we want to be able to regenerate the same code for the same author/series.
    If there is overlap between the "standard cutter codes" and the "author/series codes", we remove the "standard cutter codes" where they overlap
    :param location: The location for which to get the CutterCodeRanges
    :param starting_letter: The starting-letter for which we're looking for the codes
    :param exclude_creator_list: Which creators should be excluded from the search
    :param exclude_locationnumber_id_in: Which LocationNumbers should be excluded from the search
    :return: A list of CutterCodeRange, ordered by number
    """
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

    results.sort(key=lambda obj: (obj.number, obj.name))

    # Remove codes from cutter table if they are out of order.
    prev = None
    for r in results:
        if prev is not None and r.name < prev.name and r.is_from_cutter_table:
            results.remove(r)
        prev = r

    results.append(CutterCodeResult(starting_letter + "ZZZZZZZZZZZZ", 99999))
    return results
