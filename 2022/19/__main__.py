import dataclasses
import datetime
import enum
import logging
import math
import os
import re
import typing

from ..common import lines

logger = logging.getLogger(__name__)


class Resource(enum.Enum):
    Ore = enum.auto()
    Clay = enum.auto()
    Obsidian = enum.auto()
    Geode = enum.auto()


@dataclasses.dataclass
class BluePrint:
    identifier: int
    ore: typing.Dict[Resource, int] = dataclasses.field(default_factory=dict)
    clay: typing.Dict[Resource, int] = dataclasses.field(default_factory=dict)
    obsidian: typing.Dict[Resource, int] = dataclasses.field(default_factory=dict)
    geode: typing.Dict[Resource, int] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_description(cls, line: str) -> "BluePrint":
        """Parse a blueprint description."""
        identifier, ore, clay, obsidian, geode = line.split("Each")

        def costs(robot_string: str) -> typing.Iterable[tuple]:
            _, _, costs = robot_string.partition("costs")
            for cost in costs.split("and"):
                number, resource = cost.strip(". \n").split()
                yield Resource[resource.capitalize()], int(number)

        return cls(
            identifier=int(identifier.replace(": ", "").split(" ")[-1]),
            ore=dict(costs(ore)),
            clay=dict(costs(clay)),
            obsidian=dict(costs(obsidian)),
            geode=dict(costs(geode)),
        )


@dataclasses.dataclass
class State:
    """Exhaustive representation of a state of the extraction process.

    Attributes:
        * remaining_time: the time remaining to extract geodes
        * resources: a mapper containing the number of each resource
        * robots: a mapper containing the number of each robots (each robot is
          identified with the extracted resource)
    """

    remaining_time: int = 24

    resources: typing.Dict[Resource, int] = dataclasses.field(default_factory=dict)
    robots: typing.Dict[Resource, int] = dataclasses.field(
        default_factory=lambda: {Resource.Ore: 1}
    )


def get_next_state(
    state: State,
    robot: Resource,
    blueprint: BluePrint,
) -> typing.Optional[State]:
    """
    Compute the earliest state where the `robot` will be built, or None if the robot
    cannot be built within the remaining time.
    """
    robots = {**state.robots, robot: 1 + state.robots.get(robot, 0)}
    used_resources = {
        resource: quantity
        for resource, quantity in getattr(blueprint, robot.name.lower()).items()
        if quantity > 0
    }

    def produces(resource: Resource) -> bool:
        return state.robots.get(resource, 0) > 0

    def has_enough(resource: Resource) -> bool:
        return state.resources.get(resource, 0) >= used_resources.get(resource, 0)

    if not all(
        produces(resource) or has_enough(resource) for resource in used_resources
    ):
        return None

    elapsed_time = 1 + max(
        math.ceil(
            (used_resources.get(resource, 0) - state.resources.get(resource, 0))
            / state.robots[resource]
        )
        for resource in used_resources
    )
    if elapsed_time > state.remaining_time:
        return None

    # Accumulate resources and discard those used to build the robot
    resources = {
        resource: state.resources.get(resource, 0)
        + elapsed_time * state.robots.get(resource, 0)
        - used_resources.get(resource, 0)
        for resource in Resource
    }
    return State(
        remaining_time=state.remaining_time - elapsed_time,
        resources=resources,
        robots=robots,
    )


def accumulate(state: State) -> State:
    """Accumulate resources until no more time remains."""
    return State(
        remaining_time=0,
        resources={
            resource: state.resources.get(resource, 0)
            + state.remaining_time * state.robots.get(resource, 0)
            for resource in Resource
        },
        robots=state.robots,
    )


def max_extracted_geodes(
    blueprint: BluePrint,
    state: typing.Optional[State] = None,
    maximum_number_of_robots: typing.Optional[int] = None,
) -> int:
    """Compute the maximal number of extracted geodes for this blueprint.

    Args:
        * maximum_number_of_robots: an overall maximum number of robots of each type.
          Use it to constrain the path search.
    """
    start_time = datetime.datetime.now()

    if state is None:
        state = State()

    # No use building more robots than the maximal number of needed resource
    # produced by this robot.
    bounds = {
        resource: max(
            getattr(blueprint, robot.name.lower()).get(resource, 0)
            for robot in Resource
        )
        for resource in Resource
    }
    if maximum_number_of_robots:
        bounds = {
            resource: min(bound, maximum_number_of_robots)
            for resource, bound in bounds.items()
        }
    bounds[Resource.Geode] = state.remaining_time + 1  # Unbounded

    def _max_extracted_geodes(
        blueprint: BluePrint,
        state: State,
        bounds: dict,
        prefix: tuple = tuple(),
    ) -> tuple:
        """Recursively compute the maximal number of extracted geodes."""
        logger.debug(state.robots)

        if state.remaining_time == 0:
            # No more geodes to extract
            return state.resources.get(Resource.Geode, 0), prefix

        # Compute the next state for each choice of next robot to build
        next_states = {
            robot: get_next_state(
                state,
                robot=robot,
                blueprint=blueprint,
            )
            for robot in Resource
            if state.robots.get(robot, 0) < bounds[robot]
        }

        # Only retain the path for which we could actually build a robot
        next_states = {
            robot: next_state for robot, next_state in next_states.items() if next_state
        }
        # Last possibility: don't build any robot and accumulate resources
        next_states[None] = accumulate(state)

        # Add in possible geodes extracted during this state
        geodes = (
            _max_extracted_geodes(
                blueprint=blueprint,
                state=next_state,
                bounds=bounds,
                prefix=prefix + (robot,),
            )
            for robot, next_state in next_states.items()
        )
        return max(geodes, key=lambda k: k[0])

    geodes, path = _max_extracted_geodes(blueprint, state=state, bounds=bounds)
    elapsed_time = datetime.datetime.now() - start_time
    logger.debug(f"BluePrint {blueprint.identifier}: {geodes} geodes")
    logger.debug(f"Optimal strategy: {path}")
    logger.debug(f"Elapsed time: {elapsed_time}")
    return geodes


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    filepath = os.path.join(os.path.dirname(__file__), "input")

    def quality(blueprint: BluePrint) -> int:
        return blueprint.identifier * max_extracted_geodes(
            blueprint, maximum_number_of_robots=10
        )

    blueprints = [BluePrint.from_description(line) for line in lines(filepath)]
    # total_quality = sum(quality(blueprint) for blueprint in blueprints)
    # print(f"Total quality: {total_quality}")

    # Part 2
    a, b, c = (
        max_extracted_geodes(blueprint, state=State(remaining_time=32))
        for blueprint in blueprints[:3]
    )
    print(f"Product of geode quantities: {a * b * c}")
