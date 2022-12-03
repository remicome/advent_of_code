import dataclasses
import os
import string

from ..common import lines


@dataclasses.dataclass
class Rucksack:
    left_compartment: set
    right_compartment: set

    @classmethod
    def from_string(cls, description: str) -> "Rucksack":
        """Fill the rucksack from its description."""
        compartment_size = len(description) // 2
        return cls(
            left_compartment=set(description[:compartment_size]),
            right_compartment=set(description[compartment_size:]),
        )


def common_item(rucksack: Rucksack) -> str:
    """Unique common element found in both rucksack compartments."""
    intersection = rucksack.left_compartment & rucksack.right_compartment
    assert len(intersection) == 1
    return intersection.pop()


def priority(letter: str) -> int:
    """Return the priority for this letter."""
    assert len(letter) == 1 and letter in string.ascii_letters

    if letter.islower():
        return 1 + string.ascii_lowercase.index(letter)
    else:
        return 27 + string.ascii_uppercase.index(letter)


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    rucksacks = (Rucksack.from_string(line) for line in lines(filepath))
    common_items = (common_item(rucksack) for rucksack in rucksacks)
    priorities = (priority(common_item) for common_item in common_items)
    print(f"Total priorities: {sum(priorities)}")
