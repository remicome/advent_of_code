import json
import os
import typing


def pairs(filepath) -> typing.Iterable[tuple]:
    """Iterate on paquet pairs."""
    with open(filepath, "r") as f:
        while True:
            left = json.loads(f.readline())
            right = json.loads(f.readline())
            yield left, right

            if not f.readline():
                # We've reached the end of file
                break


def compare(
    left: typing.Union[int, list],
    right: typing.Union[int, list],
) -> typing.Optional[bool]:
    """True if the pair is correctly ordered, None if the inputs cannot be compared"""
    if isinstance(left, int) and isinstance(right, int):
        return None if left == right else left < right

    if isinstance(left, int) and isinstance(right, list):
        return compare([left], right)

    if isinstance(left, list) and isinstance(right, int):
        return compare(left, [right])

    if isinstance(left, list) and isinstance(right, list):
        for left_value, right_value in zip(left, right):
            comparison = compare(left_value, right_value)
            if comparison is None:
                continue
            else:
                return comparison
        # We ran out of items to compare -> check list lengths for a final decision
        return None if len(left) == len(right) else len(left) < len(right)

    raise ValueError


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    comparisons = (compare(left, right) for left, right in pairs(filepath))
    sum_of_indices = sum(
        i + 1 for i, comparison in enumerate(comparisons) if comparison
    )
    print(f"Sum of indices of ordered pairs: {sum_of_indices}")
