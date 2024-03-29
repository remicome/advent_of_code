import pathlib

from . import part_one, part_two

if __name__ == "__main__":
    input_path = pathlib.Path(__file__).parent / "input"

    first_sum = part_one.total_points(input_path)
    print(f"[Part 1] Total card points: {first_sum}")

    second_sum = part_two.total_scratchcards(input_path)
    print(f"[Part 2] Total scratchcards: {second_sum}")
