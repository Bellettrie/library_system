# Which numbers to consider as candidates for a book-code?
from book_code_generation.helpers import normalize_number

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
