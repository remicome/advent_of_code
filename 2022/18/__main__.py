import logging
import os
import typing

import numpy as np

from ..common import lines

logger = logging.getLogger(__name__)


def coordinates(lines: typing.Iterable[str]) -> typing.Iterable[tuple]:
    for line in lines:
        x, y, z = line.split(",")
        yield int(x), int(y), int(z)


def lava_surface(filepath: str) -> int:
    """Solve part 1 by computing the total lava surface."""
    lava = embedding(coordinates(lines(filepath)))
    return surface(lava)


def outer_lava_surface(filepath: str) -> int:
    """Solve part 2 by computing the total outer lava surface."""
    lava = embedding(coordinates(lines(filepath)))
    return surface(lava) - surface(inner_blocks(lava))


def embedding(coordinates: typing.Iterable[str]) -> np.ndarray:
    """
    Embed the object described by coordinates into a 3D cube with empty
    boundaries.
    """
    coordinates_ = list(translate(coordinates))

    # Pad input with a length-1 empty boundary on each side
    x, y, z = dimensions(coordinates_)
    embedding = np.full((x + 2, y + 2, z + 2), fill_value=False)
    embedding[
        [x + 1 for x, y, z in coordinates_],
        [y + 1 for x, y, z in coordinates_],
        [z + 1 for x, y, z in coordinates_],
    ] = True
    return embedding


def translate(coordinates: typing.Iterable[tuple]):
    """Translate coordinates so that the lowest x, y, z are all 0"""
    coordinates_ = list(coordinates)
    xmin = min(x for x, y, z in coordinates_)
    ymin = min(y for x, y, z in coordinates_)
    zmin = min(z for x, y, z in coordinates_)

    for x, y, z in coordinates_:
        yield x - xmin, y - ymin, z - zmin


def dimensions(coordinates: typing.Iterable[tuple]) -> tuple:
    """Get the input bounds."""
    coordinates = list(coordinates)
    return (
        1 + max(x for x, y, z in coordinates) - min(x for x, y, z in coordinates),
        1 + max(y for x, y, z in coordinates) - min(y for x, y, z in coordinates),
        1 + max(z for x, y, z in coordinates) - min(z for x, y, z in coordinates),
    )


def surface(embedding: np.ndarray) -> int:
    """Count the total surface, i.e. number of cube sides seeing the outside."""
    embedding = embedding.astype(int)
    exposed_sides = (
        np.sum(np.abs(np.diff(embedding, axis=axis))) for axis in (0, 1, 2)
    )
    return sum(exposed_sides)


def obstacle_free_diffusion(fluid: np.ndarray) -> np.ndarray:
    """
    Simulate a single diffusion step for a fluid which expand to every adjacent cube.
    """
    front_diffusion = np.diff(fluid, prepend=0, axis=0)
    rear_diffusion = np.diff(fluid[::-1], prepend=0, axis=0)[::-1]
    left_diffusion = np.diff(fluid, prepend=0, axis=1)
    right_diffusion = np.diff(fluid[:, ::-1], prepend=0, axis=1)[:, ::-1]
    top_diffusion = np.diff(fluid, prepend=0, axis=2)
    bottom_diffusion = np.diff(fluid[:, :, ::-1], prepend=0, axis=2)[:, :, ::-1]

    diffusion = np.concatenate(
        (
            np.expand_dims(front_diffusion, axis=-1),
            np.expand_dims(rear_diffusion, axis=-1),
            np.expand_dims(left_diffusion, axis=-1),
            np.expand_dims(right_diffusion, axis=-1),
            np.expand_dims(top_diffusion, axis=-1),
            np.expand_dims(bottom_diffusion, axis=-1),
        ),
        axis=-1,
    )

    return fluid | np.any(diffusion, axis=-1)


def diffusion(fluid: np.ndarray, rock: np.ndarray) -> np.ndarray:
    """
    Simulate a single diffusion step for a fluid which expand to every adjacent empty
    cube.
    """
    return obstacle_free_diffusion(fluid) & ~rock


def fill(fluid: np.ndarray, rock: np.ndarray) -> np.ndarray:
    """Use `fluid` as an initial state to completely fill the array."""
    last_state = False
    step = 0
    while not (fluid == last_state).all():
        step += 1
        last_state = fluid
        fluid = diffusion(fluid, rock)

    logger.debug(f"Achieved filling in {step} steps.")

    return fluid


def inner_blocks(lava: np.ndarray) -> np.ndarray:
    """
    Identify inner blocks by simulating a fluid diffusion starting from the edges.
    The diffusion is pursued until an equilibrium state is reached. Any block which is
    neither fluid nor lava is then an interior block.
    """
    # Initial state for the fluid: all boundaries are filled
    fluid = np.full(lava.shape, False)
    fluid[0] = True
    fluid[-1] = True
    fluid[:, 0] = True
    fluid[:, -1] = True
    fluid[:, :, 0] = True
    fluid[:, :, -1] = True

    lava = lava.astype(bool)
    if (fluid & lava).any():
        raise ValueError("Lava block should have empty boundaries")

    final_fluid_state = fill(fluid, rock=lava)
    return ~lava & ~final_fluid_state


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    filepath = os.path.join(os.path.dirname(__file__), "input")

    # Part 1
    print(f"Total laval surface: {lava_surface(filepath)}")

    # Part 2
    print(f"Outer laval surface: {outer_lava_surface(filepath)}")
