import dataclasses
import enum
import logging
import pathlib
import string
import typing

logger = logging.getLogger(__name__)


class Direction(enum.Enum):
    Right = 0
    Down = 1
    Left = 2
    Up = 3

    def rotate(self, clockwise: bool = True) -> "Direction":
        offset = 1 if clockwise else -1
        return Direction((self.value + offset) % 4)


@dataclasses.dataclass
class Tile:
    """One tile on the board."""

    x: int
    y: int
    wall: bool

    up: typing.Optional["Tile"] = dataclasses.field(repr=False, default=None)
    down: typing.Optional["Tile"] = dataclasses.field(repr=False, default=None)
    left: typing.Optional["Tile"] = dataclasses.field(repr=False, default=None)
    right: typing.Optional["Tile"] = dataclasses.field(repr=False, default=None)


@dataclasses.dataclass
class Adventurer:
    """An adventurer wandering through the map."""

    tile: Tile
    direction: Direction

    @classmethod
    def starting_position(cls, board) -> "Adventurer":
        """Instantiate an adventurer at its start position."""
        tile = min(
            (tile for tile in board if tile.y == 1 and not tile.wall),
            key=lambda tile: tile.x,
        )
        return cls(
            tile=tile,
            direction=Direction.Right,
        )

    def walk(self, steps: int = 1) -> "Adventurer":
        """Walk one step"""
        tile = self.tile
        for _ in range(steps):
            next_tile = getattr(tile, self.direction.name.lower())
            if next_tile.wall:
                # Stop there
                break
            else:
                tile = next_tile
        return dataclasses.replace(self, tile=tile)

    def rotate(self, clockwise: bool = True) -> "Adventurer":
        """Turn 90 degrees clockwise (the default) or counter-clockwise."""
        return dataclasses.replace(
            self,
            direction=self.direction.rotate(clockwise=clockwise),
        )


def board(filepath):
    """Parse the board and register the graph edges"""
    with open(filepath, "r") as f:
        grid, _ = f.read().split("\n\n")
    lines = grid.split("\n")

    rows = []
    for y, line in enumerate(lines):
        row = []
        for x, character in enumerate(line):
            if character in (".", "#"):
                row.append(
                    Tile(
                        x=1 + x,
                        y=1 + y,
                        wall=character == "#",
                    )
                )
        rows.append(row)

    # Map left/right neighbours
    for row in rows:
        sorted_row = sorted(row, key=lambda tile: tile.x)
        for i, tile in enumerate(sorted_row):
            tile.left = sorted_row[(i - 1) % len(row)]
            tile.right = sorted_row[(i + 1) % len(row)]

    tiles = sum(rows, start=[])

    # Map up/down neighbours
    xmax = max(tile.x for tile in tiles)
    columns = [list() for _ in range(xmax + 1)]
    for tile in tiles:
        columns[tile.x - 1].append(tile)
    for column in columns:
        sorted_column = sorted(column, key=lambda tile: tile.y)
        for y, tile in enumerate(sorted_column):
            tile.down = sorted_column[(y + 1) % len(column)]
            tile.up = sorted_column[(y - 1) % len(column)]

    return tiles


def moves(filepath) -> typing.Iterable:
    """Yield successive moves."""
    with open(filepath, "r") as f:
        _, moves = f.read().split("\n\n")
        number = ""
        for character in moves:
            if character in ("R", "L", "\n") and number:
                yield int(number)
                number = ""
            if character in ("R", "L"):
                yield character
            if character in string.digits:
                number += character


def password(adventurer: Adventurer) -> int:
    """Decode the final password"""
    return 1000 * adventurer.tile.y + 4 * adventurer.tile.x + adventurer.direction.value


def adventurer_positions(moves: typing.Iterable, board) -> typing.Iterable[Adventurer]:
    """Iterate through successive adventurer positions."""

    adventurer = Adventurer.starting_position(board)
    logger.debug(f"Starting position: {adventurer}")
    yield adventurer
    for move in moves:
        if isinstance(move, int):
            logger.debug(f"Walk {move}")
            adventurer = adventurer.walk(steps=move)
        if isinstance(move, str):
            rotation = "clockwise" if move == "R" else "counterclockwise"
            logger.debug(f"Rotate {rotation}")
            adventurer = adventurer.rotate(clockwise=move == "R")
        logger.debug(f"Adventurer position: {adventurer}")
        yield adventurer


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    filepath = pathlib.Path(__file__).parent / "test_input"
    for adventurer in adventurer_positions(moves(filepath), board=board(filepath)):
        pass

    print(f"Final password: {password(adventurer)}")
