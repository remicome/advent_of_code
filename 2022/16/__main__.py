import dataclasses
import datetime
import itertools
import logging
import os
import re
import typing

import networkx as nx

from ..common import lines

logger = logging.getLogger(__name__)


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


def relieved_pressure(
    valves: tuple,
    graph: nx.Graph,
    origin: str = "AA",
    time: int = 30,
    distance: typing.Optional[dict] = None,
) -> int:
    """
    Compute the total relieved pressure if we open the `valves` in listed order,
    starting at `origin` and taking the shortest possible path between any two valves.
    """
    if distance is None:
        distance = nx.floyd_warshall(graph)

    if valves and valves[-1] is None:
        # Special case: valves may be terminated by a None suffix, meaning that this
        # path will not be branched upon during optimization.
        valves = valves[:-1]

    def open_valve(origin: str, target: str, starting_time: int) -> tuple:
        """Open a single valve. Return a tuple (relieved_pressure, remaining_time)."""
        remaining_time = starting_time - int(distance[origin][target]) - 1
        total_relieved_pressure = remaining_time * graph.nodes[target]["flow_rate"]
        return total_relieved_pressure, remaining_time

    relieved_pressure = 0
    remaining_time = time
    for target in valves:
        logger.debug(f"Remaining time: {time} minutes.")
        pressure, remaining_time = open_valve(origin, target, starting_time=time)
        if time <= 0:
            logger.debug("Not enough remaining time")
            # We don't have time to open this valve!
            break
        relieved_pressure += pressure
        origin = target  # Register the move
        time = remaining_time
        logger.debug(
            f"Opening {target}: adding {pressure} units of relieved pressure; "
            f"total: {relieved_pressure}"
        )

    return relieved_pressure, remaining_time


def upper_bound(
    prefix: tuple,
    graph: nx.Graph,
    origin: str = "AA",
    time: int = 30,
    distance: typing.Optional[dict] = None,
) -> int:
    """
    Upper bound on the total relieved pressure we may achieve if we open all
    valves.
    """
    if distance is None:
        distance = nx.floyd_warshall(graph)

    prefix_pressure, prefix_time = relieved_pressure(
        prefix, origin=origin, time=time, graph=graph, distance=distance
    )

    # From here on, open all remaining valves
    remaining_valves = [
        node
        for node in graph.nodes
        if graph.nodes[node]["flow_rate"] > 0 and node not in prefix
    ]
    if not remaining_valves:
        return prefix_pressure

    origin = prefix[-1]
    min_distance = min(distance[origin][valve] for valve in remaining_valves)
    total_flow_rate = sum(graph.nodes[valve]["flow_rate"] for valve in remaining_valves)
    remaining_time = prefix_time - int(min_distance) - 1
    if remaining_time <= 0:
        remaining_pressure = 0
    else:
        remaining_pressure = remaining_time * total_flow_rate

    return prefix_pressure + remaining_pressure


def branch(prefix: tuple, graph: nx.Graph) -> typing.List[tuple]:
    """Branch on a given prefix by appending all valves which are not in it."""
    # Only list valves whose opening makes sense
    return [
        prefix + (valve,)
        for valve in graph.nodes
        if graph.nodes[valve]["flow_rate"] > 0 and valve not in prefix
    ]


def branch_and_bound(graph: nx.Graph) -> tuple:
    """Implement a branch and bound algorithm to find the optimal path."""
    prefixes = branch(tuple(), graph=graph)
    queue = list(prefixes)

    distance = nx.floyd_warshall(graph)

    current_max = 0
    best_path = tuple()
    while queue:
        prefix = queue.pop()
        if upper_bound(prefix, graph=graph, distance=distance) < current_max:
            # Exclude this branch
            continue
        pressure, remaining_time = relieved_pressure(
            prefix,
            graph=graph,
            distance=distance,
        )
        if pressure > current_max:
            best_path = prefix
            current_max = pressure

        if remaining_time <= 0:
            # This prefix cannot be expanded anymore
            continue
        else:
            # Branch: add possible continuation valves to open
            queue += branch(prefix, graph=graph)

    return current_max, best_path


# ===============  Part 2  ===================================
def upper_bound2(
    left_prefix: tuple,
    right_prefix: tuple,
    graph: nx.Graph,
    origin: str = "AA",
    time: int = 26,
    distance: typing.Optional[dict] = None,
) -> int:
    """
    Upper bound on the total relieved pressure we may achieve if we open all
    valves.
    """
    if distance is None:
        distance = nx.floyd_warshall(graph)

    left_pressure, left_time = relieved_pressure(
        left_prefix, origin=origin, time=time, graph=graph, distance=distance
    )
    right_pressure, right_time = relieved_pressure(
        right_prefix, origin=origin, time=time, graph=graph, distance=distance
    )

    # From here on, open all remaining valves
    remaining_valves = [
        node
        for node in graph.nodes
        if graph.nodes[node]["flow_rate"] > 0 and node not in left_prefix + right_prefix
    ]
    if not remaining_valves:
        return left_pressure + right_pressure

    left_origin = left_prefix[-1] if left_prefix and left_prefix[-1] else origin
    right_origin = right_prefix[-1] if right_prefix and right_prefix[-1] else origin
    min_distance = min(
        min(distance[left_origin][valve] for valve in remaining_valves),
        min(distance[right_origin][valve] for valve in remaining_valves),
    )
    total_flow_rate = sum(graph.nodes[valve]["flow_rate"] for valve in remaining_valves)
    remaining_time = max(left_time, right_time) - int(min_distance) - 1
    if remaining_time <= 0:
        remaining_pressure = 0
    else:
        remaining_pressure = remaining_time * total_flow_rate

    return left_pressure + right_pressure + remaining_pressure


def branch2(
    left_prefix: tuple,
    right_prefix: tuple,
    graph: nx.Graph,
) -> typing.Iterable[tuple]:
    """Branch on a two parallel prefixes by appending all valves which are not in it.

    A prefix terminating with `None` means that this path will not be continued.
    """
    # Only list valves whose opening makes sense
    available_valves = [
        valve
        for valve in graph.nodes
        if graph.nodes[valve]["flow_rate"] > 0
        and valve not in left_prefix + right_prefix
    ]
    suffixes = available_valves + [None]

    if not (left_prefix or right_prefix):
        # Special case: use left/right symmetry to avoid exploring duplicate paths
        yield from (
            ((left_valve,), (right_valve,))
            for left_valve, right_valve in itertools.combinations(suffixes, r=2)
        )
    if left_prefix and left_prefix[-1] is None:
        # Only append nodes to the right
        yield from (
            (left_prefix, right_prefix + (valve,))
            for valve in suffixes
            if valve is not None
        )
    elif right_prefix and right_prefix[-1] is None:
        # Only append nodes to the left
        yield from (
            (left_prefix + (valve,), right_prefix)
            for valve in suffixes
            if valve is not None
        )
    else:
        # Append nodes to the two prefixes at once
        yield from (
            (left_prefix + (left_valve,), right_prefix + (right_valve,))
            for left_valve, right_valve in itertools.combinations(suffixes, r=2)
        )
        yield from (
            (left_prefix + (left_valve,), right_prefix + (right_valve,))
            for right_valve, left_valve in itertools.combinations(suffixes, r=2)
        )


def branch_and_bound2(graph: nx.Graph, time=26, heuristic_max: int = 0) -> tuple:
    """
    Implement a branch and bound algorithm to find the optimal path, using two
    parallel agents.
    """
    best_path = (tuple(), tuple())
    prefixes = branch2(*best_path, graph=graph)
    queue = list(prefixes)

    distance = nx.floyd_warshall(graph)

    current_max = heuristic_max
    while queue:
        left_prefix, right_prefix = queue.pop()
        logger.debug(f"Exploring {left_prefix}, {right_prefix}")

        bound = upper_bound2(
            left_prefix,
            right_prefix,
            time=time,
            graph=graph,
            distance=distance,
        )
        logger.debug(f"Upper bound: {bound} (current maximum: {current_max})")
        if bound < current_max:
            # Exclude this branch
            logger.debug("-----> dropping branch")
            continue
        left_pressure, left_remaining_time = relieved_pressure(
            left_prefix,
            time=time,
            graph=graph,
            distance=distance,
        )
        right_pressure, right_remaining_time = relieved_pressure(
            right_prefix,
            time=time,
            graph=graph,
            distance=distance,
        )
        pressure = left_pressure + right_pressure
        if pressure > current_max:
            logger.debug(f"Maximum update: {current_max} -> {pressure}")
            best_path = left_prefix, right_prefix
            current_max = pressure

        if (
            (left_remaining_time <= 0 and right_prefix and right_prefix[-1] is None)
            or (right_remaining_time <= 0 and left_prefix and left_prefix[-1] is None)
            or (right_remaining_time <= 0 and left_remaining_time <= 0)
        ):
            # This prefix cannot be expanded anymore
            logger.debug("cannot continue this path -> dropping branch")
            continue
        else:
            # Branch: add possible continuation valves to open
            queue += list(branch2(left_prefix, right_prefix, graph=graph))

    return current_max, best_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    filepath = os.path.join(os.path.dirname(__file__), "input")

    graph = read_graph(filepath)
    distance = nx.floyd_warshall(graph)
    max_pressure, best_path = branch_and_bound(graph)
    print(f"Maximal relieved pressure: {max_pressure}.")
    print(f"Valves to open, in order: {best_path}.")

    # We expect to perform better with two agents, even if we have less time -> use the
    # latest max as a heuristic.
    start_time = datetime.datetime.now()
    max_pressure, best_path = branch_and_bound2(graph, heuristic_max=max_pressure)
    elapsed_time = datetime.datetime.now() - start_time
    print(f"Maximal relieved pressure: {max_pressure}.")
    print(f"Valves to open, in order: {best_path}.")
    logger.info(f"Elapsed time: {elapsed_time}")
