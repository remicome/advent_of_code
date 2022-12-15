import dataclasses
import os
import re
import typing

from ..common import Point, lines


@dataclasses.dataclass
class ManhattanSphere:
    center: int
    radius: int

    def row_intersection(self, y: int) -> typing.Set[Point]:
        """Intersect the sphere with the row at position y."""
        points_on_each_side = self.radius - abs(self.center.y - y)
        if points_on_each_side < 0:
            return set()
        else:
            return {
                Point(self.center.x + x, y) for x in range(points_on_each_side + 1)
            } | {Point(self.center.x - x, y) for x in range(1, points_on_each_side + 1)}


def manhattan_distance(left: Point, right: Point) -> int:
    difference = left - right
    return abs(difference.x) + abs(difference.y)


def sensors_and_beacons(filepath) -> typing.Iterable[tuple]:
    """Sensors and beacon pairs."""
    pattern = r".*x=([-\d]+), y=([-\d]+):.*x=([-\d]+), y=([-\d]+)\n"
    for line in lines(filepath):
        match = re.match(pattern, line)
        yield (
            Point(int(match.group(1)), int(match.group(2))),
            Point(int(match.group(3)), int(match.group(4))),
        )


def numbered_of_empty_positions(filepath, y: int = 2000000) -> int:
    spheres = (
        ManhattanSphere(center=sensor, radius=manhattan_distance(sensor, beacon))
        for sensor, beacon in sensors_and_beacons(filepath)
    )
    row_intersections = (sphere.row_intersection(y=y) for sphere in spheres)
    non_empty = (intersection for intersection in row_intersections if intersection)
    covered_positions = set.union(*non_empty)

    # Return beacons at this row
    beacons = {beacon for _, beacon in sensors_and_beacons(filepath) if beacon.y == y}
    return len(covered_positions - beacons)


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    y = 2000000
    n_empty = numbered_of_empty_positions(filepath, y=y)
    print(f"Number of excluded positions at row {y}: {n_empty}")
