import dataclasses
import os
import typing

from ..common import lines

T = typing.TypeVar("T")


@dataclasses.dataclass
class Assignment:
    left: set
    right: set

    @classmethod
    def from_line(cls: typing.Type[T], line: str) -> T:
        """Parse one input line"""
        left, right = line.replace("\n", "").split(",")

        def to_range(s: str) -> range:
            start, stop = s.split("-")
            return range(int(start), int(stop) + 1)

        return cls(
            left=set(to_range(left)),
            right=set(to_range(right)),
        )


def is_redundant(assignment: Assignment) -> bool:
    """Return True if one elf's asignment fully contains the other"""
    return assignment.left <= assignment.right or assignment.right <= assignment.left


def overlaps(assignment: Assignment) -> bool:
    """Return True if one elf's asignment intersects the other."""
    return bool(assignment.left & assignment.right)


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    assignments = (Assignment.from_line(line) for line in lines(filepath))
    reduncancies = (is_redundant(assignment) for assignment in assignments)
    print(f"Redundant assignments: {sum(reduncancies)}")

    assignments = (Assignment.from_line(line) for line in lines(filepath))
    overlapping = (overlaps(assignment) for assignment in assignments)
    print(f"Overlapping assignments: {sum(overlapping)}")
