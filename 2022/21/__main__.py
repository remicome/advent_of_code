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

    @classmethod
    def from_line(cls, line: str) -> "Monkey":
        name, job = line.split(": ")
        if len(job.split()) == 1:
            return IdentityMonkey(name=name, value=int(job.strip()))
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

    def __call__(self, x: int, y: int) -> int:
        match self:
            case Operation.Add:
                return x + y
            case Operation.Subtract:
                return x - y
            case Operation.Divide:
                if x % y:
                    raise ValueError("Division result is not an integer")
                return x // y
            case Operation.Multiply:
                return x * y


@dataclasses.dataclass
class IdentityMonkey(Monkey):
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
    logging.basicConfig(level=logging.INFO)
    filepath = pathlib.Path(__file__).parent / "input"

    # Day 1
    monkeys_ = (Monkey.from_line(line) for line in lines(filepath))
    monkeys = {monkey.name: monkey for monkey in monkeys_}
    root_result = monkeys["root"](monkeys, results={})
    print(f"Result for the root monkey: {root_result}")
