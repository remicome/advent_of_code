import string
import typing

from .common import lines


def sum_of_calibration_numbers(input_path: str):
    calibration_numbers = (calibration_number(line) for line in lines(input_path))
    return sum(calibration_numbers)


def calibration_number(line: str) -> int:
    """Return the calibration number associated with a single line."""
    digits_characters = filter_digits_characters(line)
    return int(digits_characters[0] + digits_characters[-1])


def filter_digits_characters(line: str) -> str:
    """Isolate digits from other characters."""
    digits = (character for character in line if character in string.digits)
    return "".join(digits)
