import dataclasses
import os
import re
import typing

from ..common import Point, lines


def sensors_and_beacons(filepath) -> typing.Iterable[tuple]:
    """Sensors and beacon pairs."""
    pattern = r".*x=([-\d]+), y=([-\d]+):.*x=([-\d]+), y=([-\d]+)\n"
    for line in lines(filepath):
        match = re.match(pattern, line)
        yield (
            Point(int(match.group(1)), int(match.group(2))),
            Point(int(match.group(3)), int(match.group(4))),
        )


def manhattan_distance(left: Point, right: Point) -> int:
    difference = left - right
    return abs(difference.x) + abs(difference.y)


@dataclasses.dataclass
class Interval:
    """Closed interval representation."""

    start: int
    stop: int

    def __len__(self) -> int:
        return self.stop - self.start + 1

    @property
    def empty(self) -> bool:
        return self.start > self.stop


@dataclasses.dataclass
class ManhattanSphere:
    center: int
    radius: int

    def row_intersection(self, y: int) -> Interval:
        """Intersect the sphere with the row at position y."""
        points_on_each_side = self.radius - abs(self.center.y - y)
        return Interval(
            start=self.center.x - points_on_each_side,
            stop=self.center.x + points_on_each_side,
        )


def size(intervals: typing.Iterable[Interval]) -> int:
    """Size a collection of intervals."""
    return sum(len(interval) for interval in non_intersecting(intervals))


def non_intersecting(intervals: typing.Iterable[Interval]) -> typing.List[Interval]:
    """
    Convert an iterable of ranges into an equivalent iterable of non-intersecting
    ranges.
    """
    interval_list = list(intervals)
    if len(interval_list) <= 1:
        return interval_list

    lowest_interval_index = min(
        range(len(interval_list)), key=lambda i: interval_list[i].start
    )
    lowest_interval = interval_list.pop(lowest_interval_index)

    # Reindex all other ranges so that they don't intersect this one
    def difference(interval: Interval, lowest_interval=lowest_interval) -> Interval:
        return Interval(
            start=max(1 + lowest_interval.stop, interval.start),
            stop=interval.stop,
        )

    updated_intervals = (
        difference(interval, lowest_interval) for interval in interval_list
    )
    updated_intervals = (
        interval for interval in updated_intervals if not interval.empty
    )
    return [lowest_interval] + non_intersecting(updated_intervals)


def numbered_of_empty_positions(filepath, y: int = 2000000) -> int:
    spheres = (
        ManhattanSphere(center=sensor, radius=manhattan_distance(sensor, beacon))
        for sensor, beacon in sensors_and_beacons(filepath)
    )
    row_intersections = (sphere.row_intersection(y=y) for sphere in spheres)
    non_empty = (
        intersection for intersection in row_intersections if not intersection.empty
    )

    # Return beacons at this row: all beacons here have been detected by a sensor, thus is
    # on one of the spheres
    beacons_on_row = {
        beacon for _, beacon in sensors_and_beacons(filepath) if beacon.y == y
    }
    return size(non_empty) - len(beacons_on_row)


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    y = 2000000
    n_empty = numbered_of_empty_positions(filepath, y=y)
    print(f"Number of excluded positions at row {y}: {n_empty}")
