import dataclasses
import enum
import itertools
import typing


def lines(filepath: str) -> typing.Iterable[str]:
    """Stream lines from given file."""
    with open(filepath, "r") as f:
        while line := f.readline():
            yield line


class Material(enum.Enum):
    Air = enum.auto()
    Rock = enum.auto()
    Sand = enum.auto()


@dataclasses.dataclass
class Point:
    x: int
    y: int

    def __hash__(self) -> int:
        return hash((self.x, self.y))


@dataclasses.dataclass
class Cave:
    """
    A sparse representation of the cave: the cave has infinite siwe and each point is
    made of air, if not set otherwise.
    """

    data: dict

    def __getitem__(self, key) -> Material:
        return self.data.get(Point(*key), Material.Air)

    def __setitem__(self, key, value: Material):
        if value != Material.Air:
            self.data[Point(*key)] = value

    @classmethod
    def from_file(cls, filepath: str) -> "Cave":
        """Parse input file."""

        def points(line: str) -> typing.Iterable[Point]:
            for raw_point in line.split("->"):
                stripped = raw_point.replace(" ", "").replace("\n", "")
                left, right = stripped.split(",")
                yield Point(int(left), int(right))

        data = {}
        for line in lines(filepath):
            for start, stop in itertools.pairwise(points(line)):
                # Add all intermediate points
                if start.x != stop.x and start.y != stop.y:
                    raise ValueError
                xmin = min(start.x, stop.x)
                xmax = max(start.x, stop.x)
                ymin = min(start.y, stop.y)
                ymax = max(start.y, stop.y)
                for x in range(xmin, xmax + 1):
                    for y in range(ymin, ymax + 1):
                        data[Point(x, y)] = Material.Rock

        return Cave(data)

    def __repr__(self) -> str:
        """Reproduce the website's plot"""
        xmin = min(point.x for point in self.data.keys())
        xmax = max(point.x for point in self.data.keys())
        ymin = min(point.y for point in self.data.keys())
        ymax = max(point.y for point in self.data.keys())

        mapper = {
            Material.Rock: "#",
            Material.Air: ".",
            Material.Sand: "o",
        }

        def line(y) -> str:
            return "".join(mapper[self[x, y]] for x in range(xmin - 1, xmax + 2)) + "\n"

        return "".join(line(y) for y in range(ymin - 1, ymax + 2))


filepath = "test_input"
Cave.from_file(filepath)
# %%
cave.data
cave[498, 3]
cave
