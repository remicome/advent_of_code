import dataclasses
import itertools
import os
import re
import typing

from tqdm import tqdm

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

    def __and__(self, other: "Interval") -> "Interval":
        """Intersect with other closed interval"""
        return Interval(
            start=max(self.start, other.start),
            stop=min(self.stop, other.stop),
        )

    def __iter__(self) -> typing.Iterable[int]:
        yield from range(self.start, self.stop + 1)

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


def number_of_empty_positions(filepath, y: int = 2000000) -> int:
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


def beacon_position(filepath, bound: Interval = Interval(0, 4000000)) -> Point:
    """Find the distress beacon's position."""
    spheres = [
        ManhattanSphere(center=sensor, radius=manhattan_distance(sensor, beacon))
        for sensor, beacon in sensors_and_beacons(filepath)
    ]

    for y in tqdm(bound, total=len(bound)):
        row_intersections = (sphere.row_intersection(y=y) & bound for sphere in spheres)
        coverage = (
            intersection for intersection in row_intersections if not intersection.empty
        )
        # Order by minimal left bound, then iterate to find a gap between to
        # successive coverage intervals
        coverage = sorted(coverage, key=lambda interval: interval.start)

        if len(coverage) == 1 and coverage[0] != bound:
            raise NotImplementedError

        rightmost_stop = bound.start
        for interval in coverage:
            if rightmost_stop + 1 < interval.start:
                # We found the gap!
                return Point(rightmost_stop + 1, y)
            rightmost_stop = max(rightmost_stop, interval.stop)

    raise ValueError("No beacon found")


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    y = 2000000
    n_empty = number_of_empty_positions(filepath, y=y)
    print(f"Number of excluded positions at row {y}: {n_empty}")

    bound = Interval(0, 4000000)
    position = beacon_position(filepath, bound=bound)
    tuning_frequency = position.x * bound.stop + position.y
    print(f"Tuning frequency of the distress signal: {tuning_frequency}")
