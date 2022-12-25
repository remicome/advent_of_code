import pathlib
import typing

from ..common import lines


def decode(snafu: str) -> int:
    """Decode a snafu number"""
    if not snafu:
        return 0

    numbers = {
        "=": -2,
        "-": -1,
        "0": 0,
        "1": 1,
        "2": 2,
    }

    return numbers[snafu[-1]] + 5 * decode(snafu[:-1])


def encode(number: int) -> str:
    """Encode a number to snafu."""
    if number == 0:
        return "0"

    def _encode(number: int) -> str:
        """Recursively encode any number > 0."""
        if number == 0:
            # Recursion ends
            return ""

        # Map the remainder modulo 5 to the corresponding snafu number
        snafu = {
            -2: "=",
            -1: "-",
            0: "0",
            1: "1",
            2: "2",
        }

        remainder = number % 5
        if remainder < 3:
            return _encode(number // 5) + snafu[remainder]
        else:
            # number = 5q + r = 5(q + 1) + r - 5, the latter part encode the units and
            # the former can be encoded recursively
            return _encode(1 + number // 5) + snafu[remainder - 5]

    return _encode(number)


def snafu_numbers(filepath: str) -> typing.Iterable[str]:
    for line in lines(filepath):
        yield line[:-1]


if __name__ == "__main__":
    filepath = pathlib.Path(__file__).parent / "input"

    # Part 1
    total_fuel = sum(decode(snafu) for snafu in snafu_numbers(filepath))
    print(f"Total fuel (SNAFU): {encode(total_fuel)}")
