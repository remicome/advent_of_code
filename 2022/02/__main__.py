import dataclasses
import enum
import os

from ..common import lines


class Choice(enum.Enum):
    """Possible choices and their respective scores."""

    ROCK = 1
    PAPER = 2
    SCISSORS = 3


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
    def from_line(cls, line: str) -> "Round":
        """Parse one line of the strategy file."""
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

    @property
    def outcome(self) -> Outcome:
        """Round outcome."""
        beats = {
            Choice.ROCK: Choice.SCISSORS,
            Choice.PAPER: Choice.ROCK,
            Choice.SCISSORS: Choice.PAPER,
        }

        if self.choice == self.opponent_choice:
            return Outcome.DRAW

        if beats[self.choice] == self.opponent_choice:
            return Outcome.WIN

        if beats[self.opponent_choice] == self.choice:
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

    rounds = (Round.from_line(line) for line in lines(filepath))
    scores = (rnd.score for rnd in rounds)
    print(f"Total score: {sum(scores)}")
