import dataclasses
import logging
import os
import typing

from .commands import CDCommand, Command, LSCommand, read_commands
from .files import BaseFile, Directory

logger = logging.getLogger(__name__)


def walk(filepath: str) -> typing.List[BaseFile]:
    """Walk the hierarchy by reading commands from input.

    Returns the list of all encountered files.
    """
    root = Directory(name="/")
    current_directory = root
    files = [root]

    for command in read_commands(filepath):
        logging.debug(f"Current directory: {current_directory.name}")
        logger.debug(f"Command: {command}")
        if isinstance(command, CDCommand):
            if command.argument == "/":
                current_directory = root
            elif command.argument == "..":
                current_directory = current_directory.parent
            else:
                current_directory = current_directory.child(name=command.argument)
        elif isinstance(command, LSCommand):
            # Record the hierarchy for newly discovered files
            children = [
                dataclasses.replace(file, parent=current_directory)
                for file in command.files
            ]
            current_directory.children = children
            files += children
        else:
            raise ValueError

    return files


if __name__ == "__main__":
    filepath = os.path.join(os.path.dirname(__file__), "input")
    files = walk(filepath=filepath)

    size_limit = 100000
    directory_sizes = (file.size for file in files if isinstance(file, Directory))
    small_directory_sizes = (size for size in directory_sizes if size <= size_limit)
    print(f"Sum of small sizes: {sum(small_directory_sizes)}")

    total_space = 70000000
    needed_space = 30000000
    used_space = files[0].size
    minimum_deletion_size = used_space + needed_space - total_space
    possible_directory_sizes = (
        file.size
        for file in files
        if isinstance(file, Directory) and file.size >= minimum_deletion_size
    )
    print(f"Minimal deletion size: {min(possible_directory_sizes)}")
