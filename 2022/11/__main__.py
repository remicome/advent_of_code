import dataclasses
import enum
import logging
import os
import typing
from functools import reduce

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Operation:
    """Operate on the worry level."""

    operation: typing.Callable
    value: int

    def __call__(self, x: int) -> int:
        return self.operation(x, self.value)

    @classmethod
    def from_description(cls, description: str) -> "Operation":
        operations = {
            "*": lambda x, y: x * y,
            "+": lambda x, y: x + y,
            "square": lambda x, y: x * x,
        }
        left, operator, right = description.split(" ")[-3:]
        if left == "old" and right == "old":
            if operator == "*":
                operation = operations["square"]
                value = 0
            else:
                raise NotImplementedError
        elif left == "old":
            operation = operations[operator]
            value = int(right)
        else:
            raise NotImplementedError

        return cls(
            operation=operation,
            value=value,
        )


@dataclasses.dataclass
class Test:
    """Division test."""

    divider: int
    success: int
    failure: int

    def __call__(self, x: int) -> int:
        """
        If the test is succesfull, return the identifier of the success monkey;
        otherwise return the failure monkey.
        """
        if x % self.divider == 0:
            return self.success
        else:
            return self.failure

    @classmethod
    def from_description(cls, description: str) -> "Test":
        divider, success, failure = description.split("\n")[:3]

        # Ensure condition order is always the same
        assert success.startswith("    If true")
        assert failure.startswith("    If false")

        def latest_int(s: str) -> int:
            return int(s.split(" ")[-1])

        return cls(
            divider=latest_int(divider),
            success=latest_int(success),
            failure=latest_int(failure),
        )


@dataclasses.dataclass
class Monkey:
    """
    Attributes:
        * inspected_items: the number of items this money has inspected so far
    """

    identifier: int
    items: typing.List[int]
    operation: Operation
    test: Test
    inspected_items: int = dataclasses.field(init=False, default=0)

    @classmethod
    def from_description(cls, description: str) -> "Monkey":
        identifier, items, operation, *test = description.split("\n")

        identifier = int(identifier.split(" ")[-1].replace(":", ""))

        # Only keep the second half of the string, the parse numbers
        _, items = items.split(":")
        items = [int(item) for item in items.replace(" ", "").split(",")]

        return cls(
            identifier=identifier,
            items=items,
            operation=Operation.from_description(operation),
            test=Test.from_description("\n".join(test)),
        )

    def inspect(self) -> typing.Iterable[int]:
        """
        Iterate on the monkey's stash: pop the first item from this momkey's stash and
        return its updated worry level.
        """
        while self.items:
            item = self.items.pop(0)
            logger.debug(f"Monkey {self.identifier}: inspecting {item}")
            self.inspected_items += 1
            yield self.operation(item)

    def throw(self, item: int) -> int:
        """Get the recipient identifier for this item."""
        recipient = self.test(item)
        logger.debug(f"Monkey {self.identifier}: throwing {item} to {recipient}")
        return recipient

    def receive(self, item: int):
        logger.debug(f"Monkey {self.identifier}: received {item}")
        """Receive an item from another monkey. Acts inplace."""
        self.items.append(item)


def descriptions(filepath: str) -> typing.Iterable[str]:
    """Iterate on monkey descriptions."""
    with open(filepath, "r") as f:
        return f.read().split("\n\n")


def play(
    monkeys: list,
    manageable_worry_level: bool = True,
    modulo: typing.Optional[int] = None,
) -> typing.List[Monkey]:
    """Play a single round of keep away and return the updated monkey states.

    Args:
        * modulo: if not None, then all worry levels are replaced with their value
          modulo `modulo`.
    """

    def relief(item: int):
        """
        Update worry level for this item after checking that it ws not damaged by the
        monkey.
        """
        return item // 3

    for monkey in monkeys:
        for item in monkey.inspect():
            if manageable_worry_level:
                item = relief(item)
            if modulo is not None:
                item = item % modulo
            recipient = monkey.throw(item)
            monkeys[recipient].receive(item)

    inspected_items = [monkey.inspected_items for monkey in monkeys]
    logger.debug(f"Numberg of inspected items: {inspected_items}")

    return monkeys


# Day 1
if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")

    # Part 1
    monkeys = [
        Monkey.from_description(description) for description in descriptions(filepath)
    ]
    for rnd in range(20):
        monkeys = play(monkeys)

    inspected_items = (monkey.inspected_items for monkey in monkeys)
    best, second = list(sorted(inspected_items))[-2:]
    print(f"Monkey business level is {best * second}")

    # Part 2
    monkeys = [
        Monkey.from_description(description) for description in descriptions(filepath)
    ]
    # Work modulo the product of all dividers so that worry levels are manageables but
    # tests still have the same outcomes
    dividers = (monkey.test.divider for monkey in monkeys)
    divider_product = reduce(lambda x, y: x * y, dividers)
    for rnd in range(10000):
        logger.debug(f"==== Round {rnd} ====")
        monkeys = play(monkeys, manageable_worry_level=False, modulo=divider_product)

    inspected_items = (monkey.inspected_items for monkey in monkeys)
    best, second = list(sorted(inspected_items))[-2:]
    print(f"Monkey business level after 10000 unmanageable rounds: {best * second}")
