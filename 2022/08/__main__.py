import itertools
import os


def read_grid(filepath: str) -> list:
    """Read the grid of tree heights as a nested list of strings."""
    with open(filepath, "r") as f:
        input_string = f.read()

    heights = input_string.split("\n")[:-1]
    return [[int(height) for height in row] for row in heights]


def is_visible(grid: list, i: int, j: int) -> bool:
    """Is the tree at position i, j visible?"""
    west = grid[i][:j]
    east = grid[i][j + 1 :]
    north = [row[j] for row in grid[i + 1 :]]
    south = [row[j] for row in grid[:i]]

    tree = grid[i][j]
    return any(
        all(tree > other_tree for other_tree in direction)
        for direction in (west, east, north, south)
    )


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    grid = read_grid(filepath)
    visible = (
        is_visible(grid, i, j) for i, j in itertools.product(range(len(grid)), repeat=2)
    )
    print(f"Visible trees: {sum(visible)}")
