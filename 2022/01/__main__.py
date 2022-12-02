import os
import typing

from ..common import lines


def calories(lines: typing.Iterable[str]) -> typing.Iterable[int]:
    """Sum calories for each elf."""
    calories = 0
    for line in lines:
        if line != "\n":
            calories += int(line)
        else:
            yield calories
            calories = 0


if __name__ == "__main__":
    input_path = os.path.join(os.path.dirname(__file__), "input")
    sorted_calories = sorted(calories(lines(input_path)))

    max_calories = sorted_calories[-1]
    print(f"Max calories: {max_calories}")

    top_three = sum(sorted_calories[-3:])
    print(f"Sum of top-three: {top_three}")
