import dataclasses
import itertools
import logging
import os
import typing

from tqdm import tqdm

from ..common import Vector

logger = logging.getLogger(__name__)


def hot_jets(filepath) -> typing.Iterable[Vector]:
    """Iterate on hot gas jets."""
    with open(filepath, "r") as f:
        jets_description = f.read().replace("\n", "")

    for character in itertools.cycle(jets_description):
        if character == "<":
            yield Vector(-1, 0)
        elif character == ">":
            yield Vector(1, 0)
        else:
            raise ValueError(character)


@dataclasses.dataclass
class Shape:
    """A shape, a.k.a a set of points."""

    points: typing.Set[Vector] = dataclasses.field(default_factory=set)

    def __iter__(self) -> typing.Iterable[Vector]:
        yield from self.points

    def __add__(self, vector: Vector) -> "Shape":
        """Translate this shape."""
        if not isinstance(vector, Vector):
            raise ValueError
        return Shape({point + vector for point in self.points})

    def __repr__(self) -> str:
        return self.to_string()

    def to_string(
        self,
        xmin: typing.Optional[int] = None,
        xmax: typing.Optional[int] = None,
        ymin: typing.Optional[int] = None,
        ymax: typing.Optional[int] = None,
    ) -> str:
        """Convenient string representation"""
        xmin = min(point.x for point in self) if xmin is None else xmin
        xmax = max(point.x for point in self) if xmax is None else xmax
        ymin = min(point.y for point in self) if ymin is None else ymin
        ymax = max(point.y for point in self) if ymax is None else ymax

        characters = [
            ["." for _ in range(xmax - xmin + 1)] for _ in range(ymax - ymin + 1)
        ]
        for point in self:
            if xmin <= point.x <= xmax and ymin <= point.y <= ymax:
                characters[ymax - point.y][point.x - xmin] = "#"

        return "\n".join("".join(chars) for chars in characters)

    def __contains__(self, point: Vector) -> bool:
        return point in self.points

    def __or__(self, other: "Shape") -> "Shape":
        """Merge this shape with another."""
        return Shape(self.points | other.points)


def rock_shapes(n: int = 2022) -> typing.Iterable:
    """Iterate on the first n falling rocks."""
    shapes = (
        Shape({Vector(0, 0), Vector(1, 0), Vector(2, 0), Vector(3, 0)}),
        Shape({Vector(0, 1), Vector(-1, 0), Vector(0, 0), Vector(1, 0), Vector(0, -1)}),
        Shape(
            {Vector(1, 1), Vector(1, 0), Vector(-1, -1), Vector(0, -1), Vector(1, -1)}
        ),
        Shape({Vector(0, 0), Vector(0, 1), Vector(0, 2), Vector(0, 3)}),
        Shape({Vector(0, 0), Vector(1, 0), Vector(0, 1), Vector(1, 1)}),
    )
    for _, shape in zip(range(n), itertools.cycle(shapes)):
        yield shape


@dataclasses.dataclass
class RockColumn(Shape):
    """A shape with cached height."""

    height: int = dataclasses.field(init=False, default=0)

    def append(self, rock: Shape):
        """Merge this rock with the rock column."""
        self.points = self.points | rock.points
        rock_height = 1 + max(point.y for point in rock)
        self.height = max(self.height, rock_height)


def initial_position(shape, rock_column: RockColumn) -> Shape:
    """Return the initial position for this rock."""
    left_edge = min(point.x for point in shape)
    bottom_edge = min(point.y for point in shape)
    translation = Vector(
        x=2 - left_edge,
        y=rock_column.height + 3 - bottom_edge,
    )
    return shape + translation


def simulate(
    jets_input: str,
    number_of_rocks: int = 2022,
    chamber_width: int = 7,
) -> RockColumn:
    """Simulate a number of falling rocks in the chamber."""
    rock_column = RockColumn()
    jets = hot_jets(jets_input)

    for n, shape in tqdm(
        enumerate(rock_shapes(n=number_of_rocks)),
        total=number_of_rocks,
    ):
        logger.debug(f"==== Rock {n} ====")
        rock = initial_position(shape, rock_column=rock_column)
        logger.debug(
            "\n%s",
            (rock_column | rock).to_string(
                xmin=0,
                xmax=chamber_width - 1,
                ymin=max(0, rock_column.height - 10),
                ymax=rock_column.height + 5,
            ),
        )

        for jet in jets:
            # Pushed by a jet
            logger.debug(f"Jet: {jet}")
            next_position = rock + jet
            stuck_by_wall = any(
                point.x < 0 or point.x >= chamber_width for point in next_position
            )
            stuck_by_column = any(point in rock_column for point in next_position)
            if stuck_by_wall or stuck_by_column:
                logger.debug("Jet could not move the rock")
            else:
                rock = next_position
            logger.debug(
                "\n%s",
                (rock_column | rock).to_string(
                    xmin=0,
                    xmax=chamber_width - 1,
                    ymin=max(0, rock_column.height - 10),
                    ymax=rock_column.height + 5,
                ),
            )

            # Falling
            logger.debug("Falling")
            next_position = rock + Vector(0, -1)
            if any(point in rock_column or point.y < 0 for point in next_position):
                logger.debug("Coming to rest position")
                rock_column.append(rock)
                break
            else:
                rock = next_position
            logger.debug(
                "\n%s",
                (rock_column | rock).to_string(
                    xmin=0,
                    xmax=chamber_width - 1,
                    ymin=max(0, rock_column.height - 10),
                    ymax=rock_column.height + 5,
                ),
            )

    return rock_column


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    filepath = os.path.join(os.path.dirname(__file__), "input")
    rock_column = simulate(jets_input=filepath, number_of_rocks=2022)
    print(f"Column height after 2022 rocks have fallen: {rock_column.height}")
