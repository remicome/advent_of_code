import pathlib

from . import part_one, part_two

if __name__ == "__main__":
    input_path = pathlib.Path(__file__).parent / "input"

    first_sum = part_one.sum_of_calibration_numbers(input_path)
    print(f"Summed calibration numbers (part one): {first_sum}")

    second_sum = part_two.sum_of_calibration_numbers(input_path)
    print(f"Summed calibration numbers (part two): {second_sum}")
