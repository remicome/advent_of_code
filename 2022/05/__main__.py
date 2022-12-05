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


def part_one(input_string: str) -> str:
    queues_description, moves_description = input_string.split("\n\n")

    moves = (Move.from_line(line) for line in moves_description.split("\n") if line)
    queues = parse_queues(queues_description)
    for move in moves:
        queues = move.apply(queues)
    return "".join(queue[-1] for queue in queues)


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")
    with open(filepath, "r") as f:
        input_string = f.read()

    top_items = part_one(input_string)
    print(f"Top items after all moves are applied: {top_items}")
