import dataclasses
import typing


def lines(filepath: str) -> typing.Iterable[str]:
    """Stream lines from given file."""
    with open(filepath, "r") as f:
        while line := f.readline():
            yield line


@dataclasses.dataclass
class Vector:
    """A point (a.k.a vector) on the two-dimensional integer grid."""

    x: int
    y: int

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __add__(self, other) -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other) -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)


# Keep this alias for compatibility
Point = Vector
