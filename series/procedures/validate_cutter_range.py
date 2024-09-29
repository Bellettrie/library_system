from book_code_generation.location_number_creation import generate_author_number, number_between


class InvalidCutterRangeError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.message = message


def validate_cutter_range(series, custom_name, letter, number):
    """
    Verifies whether the new letter + number combination would fit this series.
    The custom_name variable is used to set the text used to decide where the series should be.
    By default, the custom_name is the title of the series, but this may be any different text string chosen by whoever is inputting this data.

    The system has a hard demand that the text string is consistent with the numbers chosen, but does not demand that the custom_name is in any way related to the series.
    """
    if letter is None or letter == "ZZZZ":
        raise InvalidCutterRangeError("Letter not set; don't forget to press 'generate'.")
    if not number or number == "0":
        raise InvalidCutterRangeError("Invalid number.")

    required_letter, beg, _, end = generate_author_number(custom_name, series.location)
    if not number_between(number, beg, end):
        raise InvalidCutterRangeError(
            "Number {num} is not valid; not between {beg} and {end} (including).".format(
                num=number, beg=beg, end=end)
        )

    if required_letter != letter:
        raise InvalidCutterRangeError(
            "Wrong letter for code, press generate again.")
    return None
