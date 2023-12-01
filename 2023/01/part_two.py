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
    number = prefix_number(line, spelling=spelling)
    if number:
        return number
    else:
        return first_number(line[1:], spelling=spelling)


def last_number(line: str) -> int:
    reversed_spelling = {number: reverse(s) for number, s in SPELLING.items()}
    return first_number(reverse(line), spelling=reversed_spelling)


def prefix_number(line: str, spelling: dict) -> typing.Optional[int]:
    """If the line starts with a number, return this number."""
    for number, spelled_number in spelling.items():
        if line.startswith(str(number)) or line.startswith(spelled_number):
            return number
    return None


def reverse(s: str) -> str:
    return s[::-1]
