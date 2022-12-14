import copy
import dataclasses
import os
import typing


def parse_ints(line: str, separator=" ") -> typing.List[int]:
    """Parse all ints from the given string, separated by separator."""
    parsed = []
    for s in line.split(separator):
        try:
            parsed.append(int(s))
        except ValueError:
            pass
    return parsed


def parse_queues(queues_description: str) -> list:
    """Parse the input file to fill up queues."""
    lines = queues_description.split("\n")
    queue_numbers = lines.pop()
    number_of_queues = parse_ints(queue_numbers)[-1]

    def parse_queue(i: int) -> list:
        """Parse the i-th queue (i.e. vertical columns)."""
        column = (line[4 * i + 1] for line in lines)
        # Top element should be in the latest position
        queue = [character for character in column if character != " "]
        queue.reverse()
        return queue

    return [parse_queue(i) for i in range(number_of_queues)]


@dataclasses.dataclass
class Move:
    depth: int
    origin: int
    target: int

    def apply(self, queues: list) -> list:
        """Apply the move and return the updated queues."""
        queues = copy.deepcopy(queues)
        origin_queue = queues[self.origin]
        target_queue = queues[self.target]
        for _ in range(self.depth):
            target_queue.append(origin_queue.pop())
        return queues

    @classmethod
    def from_line(cls, line: str) -> "Move":
        """Parse move description."""
        depth, origin, target = parse_ints(line)
        return cls(
            depth=depth,
            origin=origin - 1,  # index should start at 0
            target=target - 1,
        )


class Move9001(Move):
    """Updated move using a CrateHolder9001."""

    def apply(self, queues: list) -> list:
        """Apply the move: all crates are moved in a single step."""
        queues = copy.deepcopy(queues)
        origin_queue = queues[self.origin]
        target_queue = queues[self.target]

        target_queue += origin_queue[-self.depth :]
        queues[self.origin] = origin_queue[: -self.depth]
        return queues


def apply_all_moves(input_string: str, crate_mover: typing.Type[Move] = Move) -> str:
    """Apply all moves and return the string of top queue elements.

    Args:
        * crate_mover: move class to use
    """
    queues_description, moves_description = input_string.split("\n\n")

    moves = (
        crate_mover.from_line(line) for line in moves_description.split("\n") if line
    )
    queues = parse_queues(queues_description)
    for move in moves:
        queues = move.apply(queues)
    return "".join(queue[-1] for queue in queues)


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")
    with open(filepath, "r") as f:
        input_string = f.read()

    top_items = apply_all_moves(input_string)
    print(f"Top items after all moves are applied (CrateMover9000): {top_items}")

    top_items = apply_all_moves(input_string, crate_mover=Move9001)
    print(f"Top items after all moves are applied (CrateMover9001): {top_items}")
