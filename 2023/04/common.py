from __future__ import annotations

import dataclasses
import re
import typing

from ..common import lines


def cards(input_path) -> typing.Iterable[Card]:
    return (Card.from_line(line) for line in lines(input_path))


@dataclasses.dataclass
class Card:
    identifier: int
    winning_numbers: typing.Set[int]
    numbers: typing.Set[int]

    @classmethod
    def from_line(cls, line: str) -> Card:
        match = re.match(r"Card\s+(\d+): ([\s\d]+) \| ([\s\d]+)", line)
        identifier = int(match.group(1))
        winner_numbers_string = match.group(2)
        numbers_string = match.group(3)

        return cls(
            identifier=identifier,
            winning_numbers=parse_numbers_string(winner_numbers_string),
            numbers=parse_numbers_string(numbers_string),
        )

    @property
    def points(self) -> int:
        intersection = self.numbers & self.winning_numbers
        return 2 ** (len(intersection) - 1) if intersection else 0


def parse_numbers_string(numbers_string: str) -> typing.Set[int]:
    return set(numbers_in(numbers_string))


def numbers_in(numbers_string) -> typing.Iterable[int]:
    for single_number_string in numbers_string.split(" "):
        stripped_number_string = single_number_string.strip()
        if stripped_number_string:
            yield int(stripped_number_string)
