import os
import typing

filepath = "input"


def stream(filepath: str) -> typing.Iterable[str]:
    """Stream characters from given file"""
    with open(filepath, "r") as f:
        while character := f.read(1):
            yield character


def is_packet_start(codon: str) -> bool:
    return len(set(codon)) == 4


def index_of_earliest_packet(filepath) -> int:
    buffer = ""
    for i, character in enumerate(stream(filepath)):
        buffer = (buffer + character)[-4:]
        if is_packet_start(buffer):
            return i + 1

    raise ValueError


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")
    print(f"Earliest packet received at: {index_of_earliest_packet(filepath)}")
