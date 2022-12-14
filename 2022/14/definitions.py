import dataclasses
import enum


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

    def __add__(self, other) -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other) -> "Point":
        return Point(self.x - other.x, self.y - other.y)
