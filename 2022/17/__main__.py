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


def rock_shapes() -> typing.Iterable:
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
    while True:
        yield from shapes


@dataclasses.dataclass(repr=False)
class RockColumn(Shape):
    """A shape with cached height."""

    # Retaining the top altitude for each column allows trimming all unnecessary points
    column_tops: list = dataclasses.field(init=False)

    def __post_init__(self):
        xmin = min(point.x for point in self.points)
        xmax = max(point.x for point in self.points)
        self.column_tops = [
            max(point.y for point in self.points if point.x == column)
            for column in range(xmin, xmax + 1)
        ]

    @property
    def height(self) -> int:
        return 1 + max(self.column_tops)

    def append(self, rock: Shape):
        """Merge this rock with the rock column."""

        self.column_tops = [
            max([column_top] + [point.y for point in rock if point.x == x])
            for x, column_top in enumerate(self.column_tops)
        ]
        # Trim by removing all points lower than the lowest column top
        self.points = {
            point
            for point in self.points | rock.points
            if point.y >= min(self.column_tops)
        }


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
) -> list:
    """Simulate a number of falling rocks in the chamber."""
    rock_floor = {Vector(i, -1) for i in range(chamber_width)}
    rock_column = RockColumn(rock_floor)

    def step(
        shape: Shape,
        rock_column: RockColumn = rock_column,
        jets=hot_jets(jets_input),
    ) -> RockColumn:
        rock = initial_position(shape, rock_column=rock_column)
        logger.debug(
            "\n%s",
            (rock_column | rock).to_string(
                xmin=0,
                xmax=chamber_width - 1,
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
                ),
            )

            # Falling
            logger.debug("Falling")
            next_position = rock + Vector(0, -1)
            if any(point in rock_column for point in next_position):
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
                ),
            )

        return rock_column

    heights = [0]
    for n, shape in tqdm(enumerate(rock_shapes()), total=number_of_rocks):
        if n == number_of_rocks:
            break
        logger.debug(f"====== Rock {n} ======")
        rock_column = step(shape=shape, rock_column=rock_column)
        heights.append(rock_column.height)

    return heights


def get_periodicity(heights: list, period: typing.Optional[int] = None) -> tuple:
    """Get the start sequence and periodicity of the successive height increases."""
    diff = [y - x for x, y in itertools.pairwise(heights)]

    if period:
        # Use a pre-computed period
        periods = [period]
    else:
        periods = range(1 + len(diff) // 2)

    for period in periods:
        for start in range(1 + len(diff) // 2):
            if diff[start + period :] == diff[start:-period]:
                return diff[:start], diff[start : start + period]
    raise ValueError("No periodicity found")


def long_run_simulation(number_of_rocks: int, start: list, periodicity: list) -> int:
    """Compute the expected height, knowing the starting sequence and periodicity."""
    if number_of_rocks <= len(start):
        return sum(start[:number_of_rocks:])

    quotient = (number_of_rocks - len(start)) // len(periodicity)
    remainder = (number_of_rocks - len(start)) % len(periodicity)
    return sum(start) + quotient * sum(periodicity) + sum(periodicity[:remainder])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    filepath = os.path.join(os.path.dirname(__file__), "input")

    # Part 1
    number_of_rocks = 2022
    heights = simulate(jets_input=filepath, number_of_rocks=number_of_rocks)
    print(f"Column height after {number_of_rocks} rocks have fallen: {heights[-1]}")

    # Part 2: analyze the height sequence
    heights = simulate(jets_input=filepath, number_of_rocks=5000)
    start, periodicity = get_periodicity(heights, period=1745)
    print(f"Periodicity: {len(periodicity)}")

    number_of_rocks = 1000000000000
    long_run_result = long_run_simulation(
        number_of_rocks=number_of_rocks,
        start=start,
        periodicity=periodicity,
    )
    print(f"Column height after {number_of_rocks} rocks have fallen: {long_run_result}")
