import typing

from .common import part_numbers


def sum_of_part_numbers(input_path) -> int:
    return sum(number.value for number in part_numbers(input_path))
