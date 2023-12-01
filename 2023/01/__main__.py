import pathlib
import string
import typing


def sum_of_calibration_numbers(input_path: str):
    calibration_numbers = (calibration_number(line) for line in lines(input_path))
    return sum(calibration_numbers)


def calibration_number(line: str) -> int:
    """Return the calibration number associated with a single line."""
    digits_characters = filter_digits_characters(line)
    return int(digits_characters[0] + digits_characters[-1])


def filter_digits_characters(line: str) -> str:
    """Isolate digits from other characters."""
    digits = (character for character in line if character in string.digits)
    return "".join(digits)


def lines(input_path: str) -> typing.Iterable[str]:
    """Iterate on input lines."""
    with open(input_path, "r") as f:
        while line := f.readline():
            yield line[:-1]  # Strip out the trailing '\n'


if __name__ == "__main__":
    input_path = pathlib.Path(__file__).parent / "input"
    print(f"Summed calibration numbers: {sum_of_calibration_numbers(input_path)}")
