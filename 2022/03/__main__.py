import dataclasses
import os
import string
import typing

from ..common import lines


@dataclasses.dataclass
class Rucksack:
    left_compartment: set
    right_compartment: set

    @classmethod
    def from_string(cls, description: str) -> "Rucksack":
        """Fill the rucksack from its description."""
        # Strip trailing \n
        description = description[:-1]
        assert len(description) % 2 == 0

        compartment_size = len(description) // 2
        return cls(
            left_compartment=set(description[:compartment_size]),
            right_compartment=set(description[compartment_size:]),
        )

    @property
    def content(self) -> set:
        return self.left_compartment | self.right_compartment


def common_item(rucksack: Rucksack) -> str:
    """Unique common element found in both rucksack compartments."""
    intersection = rucksack.left_compartment & rucksack.right_compartment
    assert len(intersection) == 1
    return intersection.pop()


def badge(rucksacks: typing.List[Rucksack]) -> str:
    """Unique common element to a list of rucksacks."""
    assert len(rucksacks) == 3
    contents = (rucksack.content for rucksack in rucksacks)
    intersection = set.intersection(*contents)
    assert len(intersection) == 1
    return intersection.pop()


def priority(letter: str) -> int:
    """Return the priority for this letter."""
    assert len(letter) == 1 and letter in string.ascii_letters

    if letter.islower():
        return 1 + string.ascii_lowercase.index(letter)
    else:
        return 27 + string.ascii_uppercase.index(letter)


def groups(iterable: typing.Iterable, size: int = 3) -> typing.Iterable[list]:
    """
    Chunk given iterable into groups of `size` elements.
    """
    group = []
    for i, item in enumerate(iterable):
        group.append(item)
        if i % size == size - 1:
            yield group
            group = []

    # Yield the final group, if not empty
    if group:
        yield group


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    # Part 1
    rucksacks = (Rucksack.from_string(line) for line in lines(filepath))
    common_items = (common_item(rucksack) for rucksack in rucksacks)
    priorities = (priority(common_item) for common_item in common_items)
    print(f"Total priorities: {sum(priorities)}")

    # Part 2
    rucksacks = (Rucksack.from_string(line) for line in lines(filepath))
    badges = (badge(group) for group in groups(rucksacks, size=3))
    priorities = (priority(badge) for badge in badges)
    print(f"Total badges priorities: {sum(priorities)}")
