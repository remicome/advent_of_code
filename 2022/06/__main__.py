import os
import typing


def stream(filepath: str) -> typing.Iterable[str]:
    """Stream characters from given file"""
    with open(filepath, "r") as f:
        while character := f.read(1):
            yield character


def is_marker(codon: str, marker_length: int = 4) -> bool:
    return len(set(codon)) == marker_length


def index_of_earliest_marker(filepath, marker_length: int = 4) -> int:
    buffer = ""
    for i, character in enumerate(stream(filepath)):
        buffer = (buffer + character)[-marker_length:]
        if is_marker(buffer, marker_length=marker_length):
            return i + 1

    raise ValueError


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    earliest_packet = index_of_earliest_marker(filepath, marker_length=4)
    print(f"Earliest packet received at: {earliest_packet}")

    earliest_message = index_of_earliest_marker(filepath, marker_length=14)
    print(f"Earliest message received at: {earliest_message}")
