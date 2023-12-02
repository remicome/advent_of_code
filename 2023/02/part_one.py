from .common import Game, Sample, games

MAXIMA = Sample(
    red=12,
    green=13,
    blue=14,
)


def sum_of_possible_game_identifiers(input_path):
    return sum(game.identifier for game in possible_games(input_path))


def possible_games(input_path, maxima=MAXIMA):
    yield from (game for game in games(input_path) if is_possible(game, maxima=maxima))


def is_possible(game: Game, maxima=MAXIMA):
    return all(sample <= MAXIMA for sample in game.samples)
