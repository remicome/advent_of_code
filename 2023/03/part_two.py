import typing

from .common import part_numbers


def sum_of_gear_ratios(input_path: str) -> int:
    return sum(gear_ratios(input_path))


def gear_ratios(input_path: str) -> typing.Iterable[int]:
    star_to_adjacent_part_numbers = parse_stars(input_path)
    for number_list in star_to_adjacent_part_numbers.values():
        if len(number_list) == 2:
            yield number_list[0] * number_list[1]


def parse_stars(input_path: str) -> dict:
    """Map each star to the list of adjacent part numbers."""
    adjacent_part_numbers = {}
    for number in part_numbers(input_path):
        for star in number.adjacent_stars:
            if star not in adjacent_part_numbers:
                adjacent_part_numbers[star] = [number.value]
            else:
                adjacent_part_numbers[star].append(number.value)
    return adjacent_part_numbers
