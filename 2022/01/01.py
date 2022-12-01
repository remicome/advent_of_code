import typing


def lines(filepath: str) -> typing.Iterable[str]:
    """Stream lines from given file."""
    with open(filepath, "r") as f:
        while True:
            line = f.readline()
            if line == "":
                break
            yield line


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
    sorted_calories = sorted(calories(lines("input")))

    max_calories = sorted_calories[-1]
    print(f"Max calories: {max_calories}")

    top_three = sum(sorted_calories[-3:])
    print(f"Sum of top-three: {top_three}")
