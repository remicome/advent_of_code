import dataclasses
import itertools
import os


def read_grid(filepath: str) -> list:
    """Read the grid of tree heights as a nested list of strings."""
    with open(filepath, "r") as f:
        input_string = f.read()

    heights = input_string.split("\n")[:-1]
    return [[int(height) for height in row] for row in heights]


@dataclasses.dataclass
class Compass:
    """List of trees visible from the center of the compass in any direction.

    The trees are listed starting from the one closest to the center.
    """

    center: int
    west: list
    east: list
    north: list
    south: list

    @classmethod
    def from_position(cls, grid: list, i: int, j: int) -> "Compass":
        return cls(
            center=grid[i][j],
            west=grid[i][:j][::-1],
            east=grid[i][j + 1 :],
            south=[row[j] for row in grid[i + 1 :]],
            north=[row[j] for row in grid[:i][::-1]],
        )


def is_visible(grid: list, i: int, j: int) -> bool:
    """Is the tree at position i, j visible?"""
    compass = Compass.from_position(grid, i, j)
    return any(
        all(compass.center > other_tree for other_tree in direction)
        for direction in (compass.west, compass.east, compass.north, compass.south)
    )


def scenic_score(grid: list, i: int, j: int) -> int:
    """Compute the scenic score for this tree"""
    compass = Compass.from_position(grid, i, j)

    def n_visible(tree, direction) -> int:
        for i, other in enumerate(direction):
            if other >= tree:
                return i + 1
        return len(direction)

    return (
        n_visible(compass.center, compass.west)
        * n_visible(compass.center, compass.east)
        * n_visible(compass.center, compass.north)
        * n_visible(compass.center, compass.south)
    )


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    grid = read_grid(filepath)
    visible = (
        is_visible(grid, i, j) for i, j in itertools.product(range(len(grid)), repeat=2)
    )
    print(f"Visible trees: {sum(visible)}")

    scores = (
        scenic_score(grid, i, j)
        for i, j in itertools.product(range(len(grid)), repeat=2)
    )
    print(f"Max scenic score: {max(scores)}")
