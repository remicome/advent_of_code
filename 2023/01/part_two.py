import typing

from .common import lines

NUMBERS = list(range(1, 10))
SPELLING = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
}


def sum_of_calibration_numbers(input_path: str):
    calibration_numbers = (calibration_number(line) for line in lines(input_path))
    return sum(calibration_numbers)


def calibration_number(line: str) -> int:
    return 10 * first_number(line) + last_number(line)


def first_number(line: str, spelling=SPELLING) -> int:
    index_of_ = {
        number: index(number, line=line, spelling=spelling) for number in NUMBERS
    }
    index_of = {number: idx for number, idx in index_of_.items() if idx is not None}
    return min(index_of.keys(), key=lambda number: index_of[number])


def last_number(line: str) -> int:
    reversed_spelling = {number: reverse(s) for number, s in SPELLING.items()}
    return first_number(reverse(line), spelling=reversed_spelling)


def index(number: int, line: str, spelling=SPELLING) -> typing.Optional[int]:
    """
    Find the first occurence of the number in the given line (either as a digit of
    spelled out).
    """
    try:
        digit_index = line.index(str(number))
    except ValueError:
        digit_index = None

    try:
        string_index = line.index(spelling[number])
    except ValueError:
        string_index = None

    if string_index is None and digit_index is None:
        return None
    elif string_index is None:
        return digit_index
    elif digit_index is None:
        return string_index
    else:
        return min(digit_index, string_index)


def reverse(s: str) -> str:
    return s[::-1]
