import dataclasses
import enum
import re
import typing


@dataclasses.dataclass
class Game:
    identifier: int
    samples: typing.Iterable["Sample"]


@dataclasses.dataclass
class Sample:
    red: int
    green: int
    blue: int

    def __le__(self, other: "Sample") -> bool:
        return (
            self.red <= other.red
            and self.green <= other.green
            and self.blue <= other.blue
        )


def games(input_path) -> typing.Iterable[Game]:
    """Parse games from input."""
    for line in lines(input_path):
        match = re.match(r"Game (\d+): (.*)$", line)
        yield Game(
            identifier=int(match.group(1)),
            samples=parse_samples(match.group(2)),
        )


def parse_samples(all_samples: str) -> typing.Iterable[Sample]:
    return [parse_sample(sample) for sample in samples(all_samples)]


def parse_sample(sample: str) -> Sample:
    return Sample(
        red=number_of("red", sample=sample),
        green=number_of("green", sample=sample),
        blue=number_of("blue", sample=sample),
    )


def samples(all_samples: str) -> typing.Iterable[str]:
    return all_samples.split(";")


def number_of(color: str, sample: str) -> int:
    sample = " " + sample  # Ugly regex hack
    match = re.match(f".*\s(\\d+) {color}", sample)
    if match:
        return int(match.group(1))
    else:
        return 0


def lines(input_path: str) -> typing.Iterable[str]:
    """Iterate on input lines."""
    with open(input_path, "r") as f:
        while line := f.readline():
            yield line[:-1]  # Strip out the trailing '\n'


input_path = "2023/02/input"
list(games(input_path))
