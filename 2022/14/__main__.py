import dataclasses
import itertools
import os
import typing

from .cave import Cave, RockFloorCave
from .definitions import Material, Point


def falling_sand(cave: Cave, start: Point = Point(500, 0)) -> typing.Iterable[Point]:
    """Iterate on successive sand position"""
    last_position = None
    current_position = start
    while current_position != last_position:
        yield current_position
        last_position = current_position

        # Find the first empty candidate position
        candidates = (
            current_position + Point(0, 1),
            current_position + Point(-1, 1),
            current_position + Point(1, 1),
        )
        for candidate in candidates:
            if cave[candidate] == Material.Air:
                current_position = candidate
                break


def rest_position(cave: Cave, start: Point = Point(500, 0)) -> typing.Optional[Point]:
    """Rest position for the falling sand. Return None if there is no rest position."""
    for position in falling_sand(cave):
        if position.y > cave.rock_floor:
            # Falling into the bottomless void
            break

    if position.y < cave.rock_floor:
        return position


def fill_cave(cave: Cave, start: Point = Point(500, 0)):
    """Fill the cave with falling sand from start position. Acts inplace"""
    while sand_position := rest_position(cave):
        cave[sand_position] = Material.Sand

        # Stop when no more sand can be added
        if sand_position == start:
            break


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    # Part 1
    cave = Cave.from_file(filepath)
    fill_cave(cave)
    print(cave)
    number_of_sand_units = sum(1 for _, material in cave if material == Material.Sand)
    print(f"Number of cases filled with sands: {number_of_sand_units}")

    # Part 2
    cave = RockFloorCave.from_file(filepath)
    fill_cave(cave)
    print(cave)
    number_of_sand_units = sum(1 for _, material in cave if material == Material.Sand)
    print(f"Number of cases filled with sands: {number_of_sand_units}")
