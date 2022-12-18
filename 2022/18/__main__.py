import os
import typing

import numpy as np

from ..common import lines


def coordinates(lines: typing.Iterable[str]) -> typing.Iterable[tuple]:
    for line in lines:
        x, y, z = line.split(",")
        yield int(x), int(y), int(z)


def translate(coordinates: typing.Iterable[tuple]):
    """Translate coordinates so that the lowest x, y, z are all 0"""
    coordinates_ = list(coordinates)
    xmin = min(x for x, y, z in coordinates_)
    ymin = min(y for x, y, z in coordinates_)
    zmin = min(z for x, y, z in coordinates_)

    for x, y, z in coordinates_:
        yield x - xmin, y - ymin, z - zmin


def dimensions(coordinates: typing.Iterable[tuple]) -> tuple:
    """Get the input bounds."""
    coordinates = list(coordinates)
    return (
        1 + max(x for x, y, z in coordinates) - min(x for x, y, z in coordinates),
        1 + max(y for x, y, z in coordinates) - min(y for x, y, z in coordinates),
        1 + max(z for x, y, z in coordinates) - min(z for x, y, z in coordinates),
    )


def surface(coordinates: typing.Iterable[tuple]) -> int:
    """Count the total surfae, i.e. number of cube sides seeing the outside."""
    cube_coordinates = list(translate(coordinates))

    # Pad input with a length-1 empty boundary on each side
    x, y, z = dimensions(cube_coordinates)
    lava = np.zeros((x + 2, y + 2, z + 2), dtype=int)
    lava[
        [x + 1 for x, y, z in cube_coordinates],
        [y + 1 for x, y, z in cube_coordinates],
        [z + 1 for x, y, z in cube_coordinates],
    ] = 1

    exposed_sides = (np.sum(np.abs(np.diff(lava, axis=axis))) for axis in (0, 1, 2))
    return sum(exposed_sides)


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    # Part 1
    cube_coordinates = coordinates(lines(filepath))
    print(f"Total laval surface: {surface(cube_coordinates)}")
