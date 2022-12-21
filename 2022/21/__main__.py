import dataclasses
import enum
import logging
import pathlib
import typing

from ..common import lines

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Monkey:
    name: str

    def __call__(self, monkeys: dict, results: dict) -> int:
        """Compute the results for this monkey. Update the results dict inplace."""
        raise NotImplementedError

    def solve(self, monkeys: dict, results: dict) -> int:
        """Solve the equation recursively."""

        def is_parent(monkey):
            return isinstance(monkey, OperationMonkey) and self.name in (
                monkey.left,
                monkey.right,
            )

        parents = [monkey for monkey in monkeys.values() if is_parent(monkey)]
        if len(parents) > 1:
            raise NotImplementedError
        elif len(parents) == 0:
            # We are at the root, this method doesn't make sense
            raise ValueError

        parent = parents[0]
        if parent.name == "root":
            # Special case: the solution is given by equality
            other_child = parent.right if self.name == parent.left else parent.left
            return monkeys[other_child](monkeys=monkeys, results=results)

        # Otherwise, solve the equation for the parent and infer the solution for this node
        parent_solution = parent.solve(monkeys=monkeys, results=results)
        if self.name == parent.left:
            right_value = monkeys[parent.right](monkeys=monkeys, results=results)
            logger.debug(
                f"Monkey {self.name}: solving {parent.left} {parent.operation.value} "
                f"{parent.right} = {parent.name} -> {parent.left} "
                f"{parent.operation.value} {right_value} = {parent_solution}."
            )
            solution = parent.operation.solve_left(parent_solution, right=right_value)
        elif self.name == parent.right:
            left_value = monkeys[parent.left](monkeys=monkeys, results=results)
            logger.debug(
                f"Monkey {self.name}: solving {parent.left} {parent.operation.value} "
                f"{parent.right} = {parent.name} -> {left_value} "
                f"{parent.operation.value} {parent.right} = {parent_solution}."
            )
            solution = parent.operation.solve_right(parent_solution, left=left_value)
        else:
            raise ValueError

        logger.debug(f"Monkey {self.name}: solution = {solution}")
        return solution

    @classmethod
    def from_line(cls, line: str) -> "Monkey":
        name, job = line.split(": ")
        if len(job.split()) == 1:
            return ConstantMonkey(name=name, value=int(job.strip()))
        else:
            left, operator, right = job.split()

            return OperationMonkey(
                name=name,
                left=left,
                right=right,
                operation=Operation(operator),
            )


class Operation(enum.Enum):
    Multiply = "*"
    Add = "+"
    Subtract = "-"
    Divide = "/"

    @staticmethod
    def safe_division(x: int, y: int) -> int:
        if x % y:
            raise ValueError("Division result is not an integer")
        return x // y

    def __call__(self, x: int, y: int) -> int:
        match self:
            case Operation.Add:
                return x + y
            case Operation.Subtract:
                return x - y
            case Operation.Divide:
                return self.safe_division(x, y)
            case Operation.Multiply:
                return x * y

    def solve_left(self, value: int, right: int) -> int:
        """Solve the equation `left ? right = value` for `left`"""
        match self:
            case Operation.Add:
                return value - right
            case Operation.Subtract:
                return value + right
            case Operation.Divide:
                return value * right
            case Operation.Multiply:
                return self.safe_division(value, right)

    def solve_right(self, value: int, left: int) -> int:
        """Solve the equation `left ? right = value` for `right`"""
        match self:
            case Operation.Add:
                return value - left
            case Operation.Subtract:
                return left - value
            case Operation.Divide:
                return self.safe_division(left, value)
            case Operation.Multiply:
                return self.safe_division(value, left)


@dataclasses.dataclass
class ConstantMonkey(Monkey):
    value: int

    def __call__(self, monkeys: dict, results: dict) -> int:
        """Compute the results for this monkey. Update the results dict inplace."""
        logger.debug(f"Monkey {self.name}: result = {self.value}.")
        results[self.name] = self.value
        return self.value


@dataclasses.dataclass
class OperationMonkey(Monkey):
    left: str
    right: str
    operation: typing.Callable[[int, int], int]

    def __call__(self, monkeys: dict, results: dict) -> int:
        """Compute the results for this monkey. Update the results dict inplace."""
        result = results.get(self.name)
        if result is None:

            left_result = results.get(self.left)
            if left_result is None:
                left_result = monkeys[self.left](monkeys, results=results)
                results[self.left] = left_result  # Redundant

            right_result = results.get(self.right)
            if right_result is None:
                right_result = monkeys[self.right](monkeys, results=results)
                results[self.right] = right_result  # Redundant

            logger.debug(
                f"Monkey {self.name}: {self.left} {self.operation.value} {self.right}"
                f"-> {left_result} {self.operation.value} {right_result}."
            )
            result = self.operation(left_result, right_result)
            logger.debug(f"Monkey {self.name}: result = {result}.")
            results[self.name] = result

        return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    filepath = pathlib.Path(__file__).parent / "input"

    # Day 1
    monkeys_ = (Monkey.from_line(line) for line in lines(filepath))
    monkeys = {monkey.name: monkey for monkey in monkeys_}
    results = {}  # Cache results for later
    root_result = monkeys["root"](monkeys, results=results)
    print(f"Result for the root monkey: {root_result}")

    # Day 2
    solution = monkeys["humn"].solve(monkeys=monkeys, results=results)
    print(f"You should shout this number: {solution}")
