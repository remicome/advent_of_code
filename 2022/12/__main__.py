import dataclasses
import os
import typing

from ..common import lines


@dataclasses.dataclass
class Point:
    x: int
    y: int

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __add__(self, other: "Point") -> "Point":
        return Point(x=self.x + other.x, y=self.y + other.y)


def distance_to(grid: dict, target: Point) -> dict:
    """Measure distance to the target iteratively."""

    def grow(measures: dict, grid: dict) -> dict:
        """
        Given a set of points whose distance to the target has been measured, compute
        the distance for all predecessors.
        """
        last_measures = {
            point: measure
            for point, measure in measures.items()
            if measure == max(measures.values())
        }
        new_measures = {
            predecessor: distance + 1
            for point, distance in last_measures.items()
            for predecessor in predecessors(point, grid)
            if predecessor not in measures
        }
        return measures | new_measures

    measures = {target: 0}
    previous_measures = {}
    while previous_measures != measures:
        previous_measures = measures
        measures = grow(measures, grid)

    return measures


def neighbours(point: Point, grid: dict) -> typing.Iterable[Point]:
    """Iterate on the points' neighbours"""
    neighbours = (
        point + offset
        for offset in (Point(-1, 0), Point(1, 0), Point(0, -1), Point(0, 1))
    )
    return (neighbour for neighbour in neighbours if neighbour in grid)


def predecessors(point: Point, grid: dict) -> typing.Iterable[Point]:
    """
    This point's predecessors: neighbours from which we can reach this point in
    one step.
    """
    return (
        neighbour
        for neighbour in neighbours(point, grid=grid)
        if (grid[point] - grid[neighbour]) <= 1
    )


def read_grid(filepath: str) -> tuple:
    """Parse the grid; return a tuple containing all heights, an origin and a target."""
    grid = {}
    for j, line in enumerate(lines(filepath)):
        for i, character in enumerate(line):
            point = Point(i, j)
            if character == "S":
                origin = point
                height = 0
            elif character == "E":
                target = point
                height = 25
            else:
                height = ord(character) - ord("a")
            grid[point] = height

    return grid, origin, target


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")
    grid, origin, target = read_grid(filepath)

    distances = distance_to(grid, target)
    print(f"Distance from origin to target: {distances[origin]}")

    shorted_hike = min(
        distance for point, distance in distances.items() if grid[point] == 0
    )
    print(f"Shorted hike: {shorted_hike}")
