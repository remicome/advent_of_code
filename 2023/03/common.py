from __future__ import annotations

import dataclasses
import string
import typing

from ..common import lines


@dataclasses.dataclass
class Number:
    value: int
    adjacent_characters: typing.List[str]


@dataclasses.dataclass
class Point:
    x: int
    y: int

    def __add__(self, other: Point) -> Point:
        return Point(self.x + other.x, self.y + other.y)


def part_numbers(input_path: str) -> typing.Iterable[Number]:
    grid = CharacterGrid.from_input(input_path)
    return (number for number in parse_numbers(grid) if is_a_part_number(number))


def is_a_part_number(number: Number) -> bool:
    return any(character != "." for character in number.adjacent_characters)


def parse_numbers(grid: CharacterGrid) -> typing.Iterable[Number]:
    for y, line in enumerate(grid):
        parsing_a_number = False
        starting_position = Point(0, 0)
        number_string = ""

        for x, character in enumerate(line):
            if character not in string.digits and not parsing_a_number:
                continue
            elif character not in string.digits and parsing_a_number:
                # End of number parsing
                yield current_parsed_number(
                    grid,
                    number_string=number_string,
                    starting_position=starting_position,
                )
                parsing_a_number = False
                number_string = ""
            elif character in string.digits and parsing_a_number:
                number_string += character

            elif character in string.digits and not parsing_a_number:
                parsing_a_number = True
                starting_position = Point(x, y)
                number_string = character

        if parsing_a_number:
            # Handle the End Of Line:
            yield current_parsed_number(
                grid,
                number_string=number_string,
                starting_position=starting_position,
            )


def current_parsed_number(
    grid: CharacterGrid,
    number_string: str,
    starting_position: Point,
) -> Number:
    adjacent_characters = read_adjacent_characters(
        grid,
        starting_position=starting_position,
        length=len(number_string),
    )
    return Number(
        value=int(number_string),
        adjacent_characters=adjacent_characters,
    )


def read_adjacent_characters(
    grid: CharacterGrid,
    starting_position: Point,
    length: int,
) -> typing.List[str]:
    above = [
        starting_position + Point(offset, 0) + Point(0, -1) for offset in range(length)
    ]
    below = [
        starting_position + Point(offset, 0) + Point(0, 1) for offset in range(length)
    ]
    left = [starting_position + Point(-1, y) for y in (-1, 0, 1)]
    right = [starting_position + Point(length, y) for y in (-1, 0, 1)]

    adjacent_positions = above + below + left + right

    return [grid[position] for position in adjacent_positions if position in grid]


class CharacterGrid:
    def __init__(self, data: list):
        self._data = data

    @property
    def _row_length(self) -> int:
        return len(self._data[0])

    @property
    def _column_length(self) -> int:
        return len(self._data)

    def __getitem__(self, position: Point) -> str:
        return self._data[position.y][position.x]

    def __iter__(self):
        yield from self._data

    @classmethod
    def from_input(cls, input_path: str):
        data = list(lines(input_path))
        return cls(data)

    def __contains__(self, position: Point) -> bool:
        return (
            position.x > 0
            and position.y > 0
            and position.x < self._row_length
            and position.y < self._column_length
        )
