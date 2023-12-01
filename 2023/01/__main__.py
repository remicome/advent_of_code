import pathlib

from .part_one import sum_of_calibration_numbers

if __name__ == "__main__":
    input_path = pathlib.Path(__file__).parent / "input"
    print(f"Summed calibration numbers: {sum_of_calibration_numbers(input_path)}")
