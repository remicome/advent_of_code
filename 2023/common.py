import typing


def lines(input_path: str) -> typing.Iterable[str]:
    """Iterate on input lines."""
    with open(input_path, "r") as f:
        while line := f.readline():
            yield line[:-1]  # Strip out the trailing '\n'
