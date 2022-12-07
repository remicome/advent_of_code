import dataclasses
import typing

from .files import BaseFile


@dataclasses.dataclass
class Command:
    argument: str
    results: typing.List[str]

    @classmethod
    def from_chunk(cls, chunk: str) -> "Command":
        """Parse command from input command chunk"""
        entry, *results = chunk.split("\n")
        parsed_entry = entry.split(" ")

        command = parsed_entry[1]
        argument = parsed_entry[2] if len(parsed_entry) > 2 else ""

        if command == "cd":
            subclass = CDCommand
        elif command == "ls":
            subclass = LSCommand
        else:
            raise ValueError(f"Wrong command: {command}")

        return subclass(
            argument=argument,
            results=[result for result in results if result],
        )


@dataclasses.dataclass
class CDCommand(Command):
    """Change directory"""


@dataclasses.dataclass
class LSCommand(Command):
    """List current directory content"""

    files: typing.List[BaseFile] = dataclasses.field(init=False)

    def __post_init__(self):
        """Parse results into files."""
        self.files = [BaseFile.from_string(result) for result in self.results]


def read_commands(filepath: str) -> typing.Iterable[Command]:
    """Yields commands from filepath."""
    chunk = ""
    with open(filepath, "r") as f:
        while line := f.readline():
            if chunk and line.startswith("$"):
                # Command is complete
                yield Command.from_chunk(chunk)
                chunk = ""
            chunk += line

        if chunk:
            yield Command.from_chunk(chunk)
