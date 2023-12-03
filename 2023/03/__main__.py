import pathlib

from . import part_one, part_two

if __name__ == "__main__":
    input_path = pathlib.Path(__file__).parent / "input"

    first_sum = part_one.sum_of_part_numbers(input_path)
    print(f"[Part 1] Summed part numbers: {first_sum}")

    second_sum = part_two.sum_of_gear_ratios(input_path)
    print(f"[Part 2] Summed gear ratios: {second_sum}")
