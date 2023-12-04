from .common import cards


def total_points(input_path) -> int:
    return sum(card.points for card in cards(input_path))
