import dataclasses
import pathlib
import typing

from ..common import Vector


@dataclasses.dataclass(frozen=True)
class Blizzard:
    position: Vector
    speed: Vector

    def __next__(self) -> "Blizzard":
        """Next blizzard position"""
        return dataclasses.replace(self, position=self.position + self.speed)


@dataclasses.dataclass
class Valley:
    """Input file parser."""

    origin: Vector
    target: Vector
    width: int
    height: int
    blizzards: set

    @classmethod
    def from_input(cls, filepath: str) -> "Valley":
        with open(filepath, "r") as f:
            lines = f.read().split("\n")[:-1]

        height = len(lines) - 2
        width = len(lines[0]) - 2

        # Top left point of the rectangle is at 0, 0
        origin = Vector(x=lines[0].index(".") - 1, y=-1)
        target = Vector(x=lines[-1].index(".") - 1, y=height)

        speed = {
            ">": Vector(1, 0),
            "<": Vector(-1, 0),
            "v": Vector(0, 1),
            "^": Vector(0, -1),
        }

        blizzards = {
            Blizzard(position=Vector(x, y), speed=speed[character])
            for y, line in enumerate(lines[1:-1])
            for x, character in enumerate(line[1:-1])
            if character != "."
        }

        return cls(
            origin=origin,
            target=target,
            height=height,
            width=width,
            blizzards=blizzards,
        )


def blizzard_positions(valley: Valley) -> typing.Iterable[set]:
    """Iterate on blizzards positions."""

    def next_position(blizzard, valley) -> Blizzard:
        next_position = next(blizzard)
        # Ensure periodicity
        return dataclasses.replace(
            next_position,
            position=Vector(
                next_position.position.x % valley.width,
                next_position.position.y % valley.height,
            ),
        )

    blizzards = valley.blizzards

    while True:
        yield blizzards
        blizzards = {next_position(blizzard, valley) for blizzard in blizzards}


def possible_positions(valley) -> typing.Iterable[set]:
    """Iterate on the set of possible positions at step n."""

    def neighbours(position: Vector, valley: Valley = valley) -> set:
        """All neighbours for this position (itself included)"""
        vectors = (
            Vector(0, 0),
            Vector(0, 1),
            Vector(1, 0),
            Vector(-1, 0),
            Vector(0, -1),
        )
        neighbours = (position + vector for vector in vectors)
        return {
            neighbour
            for neighbour in neighbours
            if neighbour in (valley.origin, valley.target)
            or (0 <= neighbour.x < valley.width and 0 <= neighbour.y < valley.height)
        }

    positions = {valley.origin}
    yield positions  # Initial position

    blizzards_iterator = blizzard_positions(valley)
    # Pass initial blizzards position: we move at the same time
    next(blizzards_iterator)
    for blizzards in blizzards_iterator:
        candidates = set.union(*(neighbours(position) for position in positions))
        positions = candidates - {blizzard.position for blizzard in blizzards}
        yield positions


def shortest_path_length(valley: Valley) -> int:
    """Return the first minute the target may be reached from origin."""
    for step, positions in enumerate(possible_positions(valley)):
        if valley.target in positions:
            break

    return step


if __name__ == "__main__":
    filepath = pathlib.Path(__file__).parent / "input"

    # Part 1
    valley = Valley.from_input(filepath)
    steps = shortest_path_length(valley)
    print(f"Valley exit may be reached in {steps} steps.")
