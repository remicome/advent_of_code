import dataclasses
import logging
import pathlib
import typing

from ..common import lines

logger = logging.getLogger(__name__)


@dataclasses.dataclass(repr=False)
class Input:
    """Unique value/position pait from the input file."""

    value: int
    position: int

    def __repr__(self) -> str:
        return repr(self.value)


def inputs(filepath: str) -> typing.Iterable[Input]:
    for position, line in enumerate(lines(filepath)):
        yield Input(value=int(line), position=position)


def mix(inputs: typing.Iterable[Input]) -> typing.List[Input]:
    """Decrypt input iterable"""

    def mix_item(item: Input, current_list: typing.List[Input]) -> typing.List[Input]:
        """Mix a single list item."""
        index = current_list.index(item)
        target_index = index + item.value
        if target_index < 0 or target_index > len(current_list):
            # Wrapping around
            target_index = target_index % (len(current_list) - 1)
        next_list = current_list.copy()
        next_list.pop(index)
        return next_list[:target_index] + [item] + next_list[target_index:]

    current_list = list(inputs)
    logger.debug("Initial arrangement:")
    logger.debug(current_list)
    for item in current_list:
        logger.debug(f"Moving item {item.position} with value {item.value}:")
        current_list = mix_item(item, current_list=current_list)
        logger.debug(current_list)

    return current_list


def grove_coordinates(inputs: typing.Iterable[Input]) -> tuple:
    mixed_values = [item.value for item in mix(inputs)]
    zero_index = mixed_values.index(0)
    indices = ((zero_index + index) % len(mixed_values) for index in (1000, 2000, 3000))
    return tuple(mixed_values[index] for index in indices)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    filepath = pathlib.Path(__file__).parent / "input"
    x, y, z = grove_coordinates(inputs(filepath))
    print(f"Coordinate sum: {x + y + z}")
