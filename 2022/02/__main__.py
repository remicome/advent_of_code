import dataclasses
import enum
import os

from ..common import lines


class Choice(enum.Enum):
    """Possible choices and their respective scores."""

    ROCK = 1
    PAPER = 2
    SCISSORS = 3

    @property
    def better(self) -> "Choice":
        """Return the better choice, i.e. the winner against this one."""
        mapper = {
            Choice.SCISSORS: Choice.ROCK,
            Choice.ROCK: Choice.PAPER,
            Choice.PAPER: Choice.SCISSORS,
        }
        return mapper[self]

    @property
    def lesser(self) -> "Choice":
        """Return the lesser choice, i.e. the loser against this one."""
        mapper = {
            Choice.ROCK: Choice.SCISSORS,
            Choice.PAPER: Choice.ROCK,
            Choice.SCISSORS: Choice.PAPER,
        }
        return mapper[self]

    def __gt__(self, other: "Choice") -> bool:
        return other == self.lesser

    def __lt__(self, other: "Choice") -> bool:
        return other == self.better


class Outcome(enum.Enum):
    """Possible outcomes and their respective scores."""

    LOSS = 0
    DRAW = 3
    WIN = 6


@dataclasses.dataclass
class Round:
    """A single round of the rock-paper-scissor tournament."""

    choice: Choice
    opponent_choice: Choice

    @classmethod
    def from_first_strategy(cls, line: str) -> "Round":
        """Parse one line of the strategy file.

        Here the letters X, Y, Z are mapped to player choices.
        """
        opponent_letter, letter = line.replace("\n", "").split(" ")

        opponent_mapper = {
            "A": Choice.ROCK,
            "B": Choice.PAPER,
            "C": Choice.SCISSORS,
        }
        mapper = {
            "X": Choice.ROCK,
            "Y": Choice.PAPER,
            "Z": Choice.SCISSORS,
        }
        return Round(
            choice=mapper[letter],
            opponent_choice=opponent_mapper[opponent_letter],
        )

    @classmethod
    def from_second_strategy(cls, line: str) -> "Round":
        """Parse one line of the strategy file.

        Here the letters X, Y, Z are mapped to desired outcomes.
        """
        opponent_letter, letter = line.replace("\n", "").split(" ")

        opponent_mapper = {
            "A": Choice.ROCK,
            "B": Choice.PAPER,
            "C": Choice.SCISSORS,
        }
        desired_outcomes = {
            "X": Outcome.LOSS,
            "Y": Outcome.DRAW,
            "Z": Outcome.WIN,
        }
        desired_outcome = desired_outcomes[letter]

        opponent_choice = opponent_mapper[opponent_letter]
        if desired_outcome == Outcome.LOSS:
            choice = opponent_choice.lesser
        elif desired_outcome == Outcome.DRAW:
            choice = opponent_choice
        else:
            choice = opponent_choice.better

        return Round(
            choice=choice,
            opponent_choice=opponent_choice,
        )

    @property
    def outcome(self) -> Outcome:
        """Round outcome."""
        if self.choice == self.opponent_choice:
            return Outcome.DRAW

        if self.choice > self.opponent_choice:
            return Outcome.WIN

        if self.opponent_choice > self.choice:
            return Outcome.LOSS

        raise ValueError(
            f"Something wrong with your choices: {self.choice}, {self.opponent_choice}"
        )

    @property
    def score(self) -> int:
        """Round score."""
        return self.choice.value + self.outcome.value


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    rounds = (Round.from_first_strategy(line) for line in lines(filepath))
    scores = (rnd.score for rnd in rounds)
    print(f"Total score (1st strategy): {sum(scores)}")

    rounds = (Round.from_second_strategy(line) for line in lines(filepath))
    scores = (rnd.score for rnd in rounds)
    print(f"Total score (2nd strategy): {sum(scores)}")
