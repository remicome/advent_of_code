import pathlib

from . import part_one

if __name__ == "__main__":
    input_path = pathlib.Path(__file__).parent / "input"

    first_sum = part_one.sum_of_part_numbers(input_path)
    print(f"[Part 1] Summed part numbers: {first_sum}")
