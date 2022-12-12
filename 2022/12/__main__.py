import dataclasses
import os
import typing

from ..common import lines


@dataclasses.dataclass
class Point:
    """A topographic point on the grid."""

    x: int
    y: int
    z: int

    def precedes(self, other: "Point") -> bool:
        """Return True if we can step from this point to other in one step."""
        neighbouring = abs(self.x - other.x) + abs(self.y - other.y) == 1
        not_too_high = (other.z - self.z) <= 1
        return neighbouring and not_too_high

    def predecessors(self, points: typing.Iterable["Point"]) -> typing.Set["Point"]:
        """
        This point's predecessors: neighrbourd from which we can reach this point in
        one step.
        """
        # FIXME: this is ugly, as we don't use the coordinates to look for neighbours
        # directly
        return {point for point in points if point.precedes(self)}

    def __hash__(self) -> int:
        """Make this hashable to use in sets and dictionnaries."""
        return hash((self.x, self.y, self.z))


def read_grid(lines: typing.Iterable[str]) -> tuple:
    """
    Parse the grid; return a tuple containing the list of all points, an origin and a
    target.
    """
    points = []
    for j, line in enumerate(lines):
        for i, character in enumerate(line):
            if character == "S":
                origin = point = Point(x=i, y=j, z=0)
            elif character == "E":
                target = point = Point(x=i, y=j, z=25)
            else:
                point = Point(x=i, y=j, z=ord(character) - ord("a"))
            points.append(point)

    return points, origin, target


def distance_to(points: typing.List[Point], target: Point) -> dict:
    """Measure distance to the target iteratively."""

    def grow(measures: dict, grid: list) -> dict:
        """
        Grow a set of points by adding its direct predecessors (points which are at
        distance one from already-measured points).
        """
        last_measures = {
            point: measure
            for point, measure in measures.items()
            if measure == max(measures.values())
        }
        new_measures = {
            predecessor: distance + 1
            for point, distance in last_measures.items()
            for predecessor in point.predecessors(grid)
            if predecessor not in measures
        }
        return measures | new_measures

    measures = {target: 0}
    previous_measures = {}
    while previous_measures != measures:
        previous_measures = measures
        measures = grow(measures, points)

    return measures


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")
    points, origin, target = read_grid(lines(filepath))

    distances = distance_to(points, target)
    print(f"Distance from origin to target: {distances[origin]}")
