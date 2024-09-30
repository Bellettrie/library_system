from book_code_generation.math import number_between
from book_code_generation.procedures.location_number_generation import generate_location_number


class InvalidCutterRangeError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def validate_cutter_range(location, name, letter, number):
    """
    Verifies whether the letter+number combo is correct for this location ánd this name.
    By default, the name would be the name of the author, or the title of a series, but this may be any different text string chosen by whoever is inputting this data.

    The system has a hard demand that the text string is consistent with the numbers chosen, but does not demand that the name is in any way related to the object receiving the letter+number.
    """
    if letter is None or letter == "UNKNOWN":
        raise InvalidCutterRangeError("Letter not set; don't forget to press 'generate'.")
    if not number or number == "0":
        raise InvalidCutterRangeError("Invalid number.")

    required_letter, beg, _, end = generate_location_number(name, location)
    if not number_between(number, beg, end):
        raise InvalidCutterRangeError(
            "Number {num} is not valid; not between {beg} and {end} (including).".format(
                num=number, beg=beg, end=end)
        )

    if required_letter != letter:
        raise InvalidCutterRangeError(
            "Wrong letter for code, press generate again.")
    return None
