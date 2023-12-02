import pathlib

from . import part_one, part_two

if __name__ == "__main__":
    input_path = pathlib.Path(__file__).parent / "input"

    first_sum = part_one.sum_of_possible_game_identifiers(input_path)
    print(f"[Part 1] Summed game numbers: {first_sum}")

    second_sum = part_two.sum_of_game_powers(input_path)
    print(f"[Part 2] Summed game powers: {second_sum}")
