import typing

from .common import Card, cards


def total_scratchcards(input_path: str) -> int:
    return sum(number_of_copies(cards(input_path)))


def number_of_copies(cards: typing.Iterable[Card]) -> typing.Iterable[int]:
    number_of_copies: typing.Dict[int, int] = {}

    for card in cards:
        yield number_of_copies.get(card.identifier, 1)

        for next_card in range(card.match_count):
            next_card_identifier = card.identifier + next_card + 1
            number_of_copies_won = number_of_copies.get(card.identifier, 1)
            current_number_of_copies = number_of_copies.get(next_card_identifier, 1)
            number_of_copies[next_card_identifier] = (
                current_number_of_copies + number_of_copies_won
            )
