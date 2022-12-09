import dataclasses
import enum
import os
import typing

from ..common import lines


@dataclasses.dataclass
class Coordinates:
    """Object coordinates on the grid."""

    x: int = 0
    y: int = 0

    def __add__(self, other):
        return Coordinates(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other):
        return Coordinates(x=self.x - other.x, y=self.y - other.y)


class Direction(enum.Enum):
    UP = "U"
    DOWN = "D"
    RIGHT = "R"
    LEFT = "L"


@dataclasses.dataclass
class Move:
    """Description of a tail move"""

    direction: Direction
    speed: int

    @classmethod
    def from_line(cls, line: str) -> "Move":
        direction, speed = line.replace("\n", "").split(" ")
        return cls(
            direction=Direction(direction),
            speed=int(speed),
        )

    def apply(self, coordinates: Coordinates) -> typing.Iterable["Coordinates"]:
        """Iterate on successive positions visited during this move."""

        def update(coordinates: Coordinates, direction: Direction, offset: int):
            if self.direction == Direction.UP:
                return dataclasses.replace(coordinates, y=coordinates.y + offset)
            if self.direction == Direction.DOWN:
                return dataclasses.replace(coordinates, y=coordinates.y - offset)
            if self.direction == Direction.RIGHT:
                return dataclasses.replace(coordinates, x=coordinates.x + offset)
            if self.direction == Direction.LEFT:
                return dataclasses.replace(coordinates, x=coordinates.x - offset)
            raise ValueError

        yield from (
            update(coordinates, self.direction, offset + 1)
            for offset in range(self.speed)
        )


@dataclasses.dataclass
class Bridge:
    """Head and tail coordinates."""

    head: Coordinates = dataclasses.field(default_factory=Coordinates)
    knots: typing.List[Coordinates] = dataclasses.field(
        default_factory=lambda: [Coordinates()]
    )

    def __post_init__(self):
        if self.knots is None:
            self.knots = [Coordinates()]

    @property
    def tail(self) -> Coordinates:
        return self.knots[-1]

    def follow(self, head) -> "Bridge":
        """Return an updated copy of the bridge tail following the head."""

        def move_knot(knot, ahead_knot) -> Coordinates:
            relative = ahead_knot - knot

            if abs(relative.x) <= 1 and abs(relative.y) <= 1:
                # Knots are touching
                offset = Coordinates(0, 0)
            elif relative.x == 0:
                offset = Coordinates(y=1 if relative.y > 0 else -1)
            elif relative.y == 0:
                offset = Coordinates(x=1 if relative.x > 0 else -1)
            else:
                # Diagonal move
                offset = Coordinates(
                    x=1 if relative.x > 0 else -1,
                    y=1 if relative.y > 0 else -1,
                )
            return knot + offset

        ahead_knot = head
        knots = []
        for knot in self.knots:
            ahead_knot = move_knot(knot, ahead_knot)
            knots.append(ahead_knot)

        return Bridge(head=head, knots=knots)


def bridges(filepath, number_of_knots=1) -> typing.Iterable[Bridge]:
    moves = (Move.from_line(line) for line in lines(filepath))

    bridge = Bridge(knots=[Coordinates() for _ in range(number_of_knots)])
    yield bridge
    for move in moves:
        for head in move.apply(bridge.head):
            bridge = bridge.follow(head)
            yield bridge


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    tail_positions = {(bridge.tail.x, bridge.tail.y) for bridge in bridges(filepath)}
    print(f"Different positions: {len(tail_positions)}")

    tail_positions = {
        (bridge.tail.x, bridge.tail.y)
        for bridge in bridges(filepath, number_of_knots=9)
    }
    print(f"Different positions with 10 knots: {len(tail_positions)}")

    filepath = os.path.join(os.path.dirname(__file__), "test_input")
