import os
import typing

from ..common import lines


def registers(instructions: typing.Iterable[str]) -> typing.Iterable[int]:
    """Iterate on the register value, following the different instructions.

    Yield the register value *during* each cycle.
    """
    # During the first cycle, the starting value is 1
    register = 1
    yield register

    for instruction in instructions:
        if instruction[:4] == "noop":
            yield register
        elif instruction[:4] == "addx":
            # This takes two cycles to complete
            yield register

            _, string_value = instruction.replace("\n", "").split(" ")
            value = int(string_value)
            register = register + value
            yield register


def pixels(registers: typing.Iterable[int], width: int = 40) -> typing.Iterable[bool]:
    """Generate per-cycle pixel values."""
    for cycle, register in enumerate(registers):
        drawing_position = cycle % width
        yield (-1 <= drawing_position - register <= 1)


def crt_lines(pixels: typing.Iterable[int], width: int = 40) -> typing.Iterable[str]:
    """Generate screen lines."""
    line = ""
    for cycle, pixel in enumerate(pixels):
        line += "█" if pixel else " "
        if cycle % width == width - 1:
            yield line
            line = ""


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    # Part 1
    cycles_to_look_for = (20, 60, 100, 140, 180, 220)
    instructions = lines(filepath)
    signal_strengths = (
        (1 + cycle) * register
        for cycle, register in enumerate(registers(instructions))
        if cycle + 1 in cycles_to_look_for
    )
    print(f"Sum of signal strengths: {sum(signal_strengths)}")

    # Part 2
    print("Screen message:")
    instructions = lines(filepath)
    registers_ = registers(instructions)
    pixels_ = pixels(registers_)
    for line in crt_lines(pixels_):
        print(line)
