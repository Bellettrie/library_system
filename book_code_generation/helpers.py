import re
import unicodedata

_ligature_re = re.compile(r'LATIN (?:(CAPITAL)|SMALL) LIGATURE ([A-Z]{2,})')


def split_ligatures(s):
    """
    Split the ligatures in `s` into their component letters.
    """

    def untie(letter):
        try:
            m = _ligature_re.match(unicodedata.name(letter))
            if not m:
                return letter
            elif m.group(1):
                return m.group(2)
            else:
                return m.group(2)
        except ValueError:
            return ""

    return ''.join(untie(c) for c in s)


def normalize_str(strs):
    """ Normalizes string in such a way that when sorted it's in the order we want. It destroys accents and merges IJ. Only works for western-like names"""
    strs = split_ligatures(strs).upper().replace("IJ", "Y").replace("ø".upper(), "O")
    data = strs
    normal = unicodedata.normalize('NFKD', data).encode('ASCII', 'ignore')
    return normal.decode('ASCII')


def normalize_number(num):
    """
    Normalize the number. Due to dirty type magics this works both on integers, and strings.
    *Example*: 370 --> 37
    """
    return str(float('0.' + str(num)))[2:]


def get_number_for_code(code: str):
    """
    Get the number from a book_code
    :param code: A book_code
    :return: Eg. 37 from SF-T-37-lr1
    """
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


STANDARD_CODE_LENGTH = 4


def standardize_code(cc: str):
    """
    Turn code with strange numbers into standardized numbers:
    SF-T-370-lr1 ==> SF-T-37-lr1
    """
    code = cc.replace(" ", "")
    code_parts = code.split("-")

    is_full_code = len(code_parts) >= STANDARD_CODE_LENGTH

    return_value = ''

    if is_full_code:
        location_part = code_parts[0]

        if location_part ==  "V":
            # If the first part is 'V', and we have a longer code, we
            location_part = "N"

        first_letter_part = code_parts[1]
        float_number_part = code_parts[2]
        # If the third part is not the last part, we use some special rules for it.
        try:
            cde = str(float("0." + float_number_part)).split(".")
            if len(cde) > 1:
                float_number_part = cde[1]
        except ValueError:
            pass
        return_value = location_part + '-' + first_letter_part + '-' + float_number_part + '-'

        # only handle the rest of the code using the standard algorithm.
        code_parts = code_parts[3:]

    for i in range(0, len(code_parts)):
        if i > 0:
            return_value += '-'
        return_value += last_code_parts_number_standardising(code_parts[i])

    return return_value.upper()


def last_code_parts_number_standardising(code_part):
    num = 0
    c = ""
    for char in code_part:
        if char in "0123456789":
            num *= 10
            num += int(char)
        else:
            if num > 0:
                c += str.rjust(str(num), 6, "0")
                num = 0
            c += char
    if num > 0:
        c += str.rjust(str(num), 6, "0")
    return c


def get_numbers_between(start, end):
    """
    Get a list of probable candidate numbers between two numbers. Observe that if start != end, there's infinitely many candidates.
    If start == end, return start.
    :param start: The number just below the range
    :param end:  The number just above the range
    :return: A list of candidate numbers

    Example: Ie. 37, 38 -> [371, 372, 373, 374, 375,376, 377, 378]
    """

    magic_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]

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
            for number in magic_numbers:
                target = runner * 10 + number
                if round(start_float * 1000) / 100 < target < round(end_float * 1000) / 100:
                    numbers.append(target)
            runner += 1
        if len(numbers) > 0:
            return numbers
    return [start]


def float_conv(number: str):
    """ Converts a book-code-number (as string or int) to a float. Mostly used for comparisons"""
    return float("0." + str(number))


def number_between(number: str, minimum: str, maximum: str):
    """ Returns whether the first argument is inbetween the second and third ones, using book code number maths."""
    number_fl = float_conv(number)
    minimum_fl = float_conv(minimum)
    maximum_fl = float_conv(maximum)
    return minimum_fl <= number_fl <= maximum_fl


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
