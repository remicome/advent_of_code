import dataclasses
import logging
import re
import typing

import networkx as nx

from ..common import lines

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@dataclasses.dataclass
class Node:
    """A node description, as given by the input file."""

    name: str
    flow_rate: int
    edges: typing.List[str]

    @classmethod
    def from_line(cls, line: str) -> "Node":
        pattern = re.compile(
            r"Valve (\w\w) has flow rate=(\d+); tunnels? leads? to valves? ([\w ,]+)"
        )
        match = re.match(pattern, line)
        return cls(
            name=match.group(1),
            flow_rate=int(match.group(2)),
            edges=match.group(3).replace(" ", "").split(","),
        )


def read_graph(filepath: str) -> nx.Graph:
    """Parse the input graph."""
    nodes = [Node.from_line(line) for line in lines(filepath)]

    graph = nx.Graph()
    graph.add_nodes_from(((node.name, {"flow_rate": node.flow_rate}) for node in nodes))
    graph.add_edges_from(
        ((node.name, target) for node in nodes for target in node.edges)
    )
    return graph


filepath = "test_input"
graph = read_graph(filepath)
distance = nx.floyd_warshall(graph)
nx.draw(graph, with_labels=True)


def relieved_pressure(
    valves: list,
    origin: str = "AA",
    time: int = 30,
    graph=graph,
    distance=distance,
):
    """
    Compute the total relieved pressure if we open the `valves` in listed order,
    starting at `origin` and taking the shortest possible path between any two valves.
    """

    def open_valve(origin: str, target: str, starting_time: int) -> tuple:
        """Open a single valve. Return a tuple (relieved_pressure, remaining_time)."""
        remaining_time = starting_time - int(distance[origin][target]) - 1
        total_relieved_pressure = remaining_time * graph.nodes[target]["flow_rate"]
        return total_relieved_pressure, remaining_time

    relieved_pressure = 0
    for target in valves:
        logger.debug(f"Remaining time: {time} minutes.")
        pressure, time = open_valve(origin, target, starting_time=time)
        if time < 0:
            logger.debug("Not enough remaining time")
            # We don't have time to open this valve!
            break
        relieved_pressure += pressure
        origin = target  # Register the move
        logger.debug(
            f"Opening {target}: adding {pressure} units of relieved pressure; "
            f"total: {relieved_pressure}"
        )

    return relieved_pressure


relieved_pressure(["DD", "BB", "JJ", "HH", "EE", "CC"], origin="AA")
