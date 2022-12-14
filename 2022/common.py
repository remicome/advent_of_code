import typing


def lines(filepath: str) -> typing.Iterable[str]:
    """Stream lines from given file."""
    with open(filepath, "r") as f:
        while line := f.readline():
            yield line
