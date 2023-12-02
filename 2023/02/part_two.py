from .common import Game, Sample, games


def sum_of_game_powers(input_path: str) -> int:
    return sum(power(game) for game in games(input_path))


def power(game: Game) -> int:
    required_cubes = minimum_required_cubes(game)
    return required_cubes.red * required_cubes.green * required_cubes.blue


def minimum_required_cubes(game) -> Sample:
    return Sample(
        red=max(sample.red for sample in game.samples),
        green=max(sample.green for sample in game.samples),
        blue=max(sample.blue for sample in game.samples),
    )
