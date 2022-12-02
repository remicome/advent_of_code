import typing


def lines(filepath: str) -> typing.Iterable[str]:
    """Stream lines from given file."""
    with open(filepath, "r") as f:
        while True:
            line = f.readline()
            if line == "":
                break
            yield line
