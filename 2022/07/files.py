import dataclasses
import typing


@dataclasses.dataclass
class BaseFile:
    """Base file class"""

    name: str
    parent: typing.Optional["Directory"] = None  # None means this is the root

    @classmethod
    def from_string(cls, line: str) -> "BaseFile":
        description, _ = line.split(" ")
        if description == "dir":
            subclass = Directory
        else:
            subclass = File

        return subclass.from_string(line)


@dataclasses.dataclass
class Directory(BaseFile):
    """A directory."""

    children: typing.List[BaseFile] = dataclasses.field(default_factory=list)

    @classmethod
    def from_string(cls, line: str) -> "Directory":
        description, name = line.split(" ")
        if description != "dir":
            raise ValueError
        return cls(name=name)

    def child(self, name: str):
        """Get a child file by name."""
        for child in self.children:
            if child.name == name:
                return child
        raise ValueError("No matching child.")

    @property
    def size(self) -> int:
        """Directory size."""
        return sum(child.size for child in self.children)


@dataclasses.dataclass
class File(BaseFile):
    """A concrecte file, with a size"""

    size: int = 0

    @classmethod
    def from_string(cls, line: str) -> "File":
        size, name = line.split(" ")
        return cls(name=name, size=int(size))
