import collections
import dataclasses
import itertools
import logging
import pathlib
import typing

import tqdm

from ..common import Vector, lines

logger = logging.getLogger(__name__)


def read_elves(filepath: str):
    """Read the elves' starting position."""
    return {
        Vector(x, y)
        for y, line in enumerate(lines(filepath))
        for x, character in enumerate(line)
        if character == "#"
    }


def initial_state(filepath: str) -> tuple:
    """Return the initial elves positions and candidate directions."""
    directions = (
        (Vector(0, -1), Vector(-1, -1), Vector(1, -1)),  # North
        (Vector(0, 1), Vector(-1, 1), Vector(1, 1)),  # South
        (Vector(-1, 0), Vector(-1, 1), Vector(-1, -1)),  # West
        (Vector(1, 0), Vector(1, 1), Vector(1, -1)),  # East
    )
    return read_elves(filepath), directions


def play_round(elves: set, directions: tuple) -> tuple:
    """Move for one round."""
    next_positions = {
        elf: next_position(elf, elves=elves, directions=directions) for elf in elves
    }
    # Only keep the actual moves
    next_positions = {
        elf: target for elf, target in next_positions.items() if elf != target
    }
    counter = collections.Counter(next_positions.values())

    def move(elf: Vector) -> Vector:
        """Only move if this is the only elf targeting this point."""
        target = next_positions.get(elf, elf)
        return target if counter.get(target, 0) < 2 else elf

    moved_elves = {move(elf) for elf in elves}
    new_directions = directions[1:] + (directions[0],)
    return moved_elves, new_directions


def next_position(elf: Vector, elves: set, directions: list) -> Vector:
    """Get the next position for this elf."""
    adjacent = {elf + offset for direction in directions for offset in direction}
    if not (adjacent & elves):
        # No adjacent elves: stay here
        return elf

    target = elf
    for direction in directions:
        candidate, left, right = direction
        if not {elf + candidate, elf + left, elf + right} & elves:
            target = elf + candidate
            break

    return target


@dataclasses.dataclass
class Bounds:
    xmin: int = 0
    xmax: int = 0
    ymin: int = 0
    ymax: int = 0


def get_bounds(elves: set) -> Bounds:
    return Bounds(
        xmin=min(elf.x for elf in elves),
        xmax=max(elf.x for elf in elves),
        ymin=min(elf.y for elf in elves),
        ymax=max(elf.y for elf in elves),
    )


def covered_empty_ground(elves: set) -> int:
    bounds = get_bounds(elves)
    covered_area = (bounds.xmax - bounds.xmin + 1) * (bounds.ymax - bounds.ymin + 1)
    return covered_area - len(elves)


def plot(elves) -> str:
    bounds = get_bounds(elves)

    def character(x, y) -> str:
        return "#" if Vector(x, y) in elves else "."

    return "\n".join(
        (
            "".join((character(x, y) for x in range(bounds.xmin, bounds.xmax + 1)))
            for y in range(bounds.ymin, bounds.ymax + 1)
        )
    )


def simulate(filepath: str) -> typing.Iterable[set]:
    """Iterate on successive elves positions."""
    elves, directions = initial_state(filepath)
    logger.debug(f"===== Initial position =====\n{plot(elves)}")
    yield elves

    n = 0
    while True:
        n += 1
        elves, directions = play_round(elves, directions)
        logger.debug(f"===== Round {n} =====\n{plot(elves)}")
        yield elves


if __name__ == "__main__":
    filepath = pathlib.Path(__file__).parent / "input"
    logging.basicConfig(level=logging.INFO)

    # Part 1: play 10 rounds
    n_rounds = 10
    for i, elves in zip(range(n_rounds + 1), simulate(filepath)):
        pass
    covered_ground = covered_empty_ground(elves)

    print(f"Covered empty ground after {n_rounds} rounds: {covered_ground} units")

    # Part 2: play until no more elves are moving
    elve_pairs = itertools.pairwise(simulate(filepath))
    round_number = 0
    for n, (last_elves, elves) in enumerate(elve_pairs):
        round_number = n + 1
        if round_number % 10 == 0:
            logger.info(f"Round {round_number}")
        if last_elves == elves:
            break
    print(f"First round where no elf moves: {round_number}")
