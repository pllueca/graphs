from dataclasses import dataclass, field
import json
from enum import IntEnum, auto
import random
import heapq

from .distance_utils import manhattan_distance


class CellState(IntEnum):
    ACTIVE = auto()
    INACTIVE = auto()
    SLOW = auto()
    CURRENT = auto()
    VISITED = auto()
    GOAL = auto()


DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]


@dataclass
class Cell:
    state: CellState = CellState.ACTIVE
    prev_state: CellState | None = None

    def change_state(self, new_state: CellState):
        self.prev_state = self.state
        self.state = new_state

    def revert_state(self):
        if not self.prev_state:
            raise Exception("no prev state")
        self.state = self.prev_state

    def make_current(self):
        self.prev_state = self.state
        self.state = CellState.CURRENT

    def make_goal(self):
        self.prev_state = self.state
        self.state = CellState.GOAL

    def flip_active(self):
        """Asume cell is either active or inactive"""
        (
            self.change_state(CellState.ACTIVE)
            if self.state == CellState.INACTIVE
            else self.change_state(CellState.INACTIVE)
        )

    def cell_cost(self) -> int:
        match self.state:
            case CellState.ACTIVE | CellState.CURRENT | CellState.GOAL:
                return 1
            case CellState.SLOW:
                return 5
            case _:
                raise Exception()


@dataclass(order=True)
class PrioritizedNeighbor:
    """Used in priority queues to sort neighbors by distance to goal."""

    distance: int
    position: tuple[int, int]


class GridGraph:

    def __init__(
        self,
        width: int,
        height: int,
        initial_position: tuple[int, int] | None = None,
        goal_position: tuple[int, int] | None = None,
        inactives: list[tuple[int, int]] = None,
    ) -> None:
        self._cells = [[Cell() for _ in range(height)] for _ in range(width)]
        self._current = None
        self._width = width
        self._height = height

        if initial_position:
            self.set_current(*initial_position)

        self._goal = goal_position
        if goal_position:
            self.at(*goal_position).make_goal()

        if inactives is not None:
            for i, j in inactives:
                self.at(i, j).change_state(CellState.INACTIVE)

    def path_cost(self, path: list[tuple[int, int]]):
        return sum([self.at(i, j).cell_cost() for i, j in path])

    def add_n_inactives(self, n: int):
        """Adds n inactive squares to the map, ensuring that there is always at least 1 path from initial to goal"""
        path = set(self.find_path_greedy_semirandom_bfs())
        inactives_set = set()
        all_possibe = [
            (i, j)
            for i in range(self._height)
            for j in range(self._width)
            if (i, j) not in path
            and self.at(i, j).state
            not in {
                CellState.CURRENT,
                CellState.GOAL,
                CellState.INACTIVE,
            }
        ]

        if n > len(all_possibe):
            n = len(all_possibe)
        inactives_set = random.sample(all_possibe, n)
        for i, j in inactives_set:
            self.at(i, j).change_state(CellState.INACTIVE)

    def make_n_paths(self, n: int):
        """
        Marks most of the squares as inactives, but leaves at least n random paths from source to dest
        """
        path = set()
        for _ in range(n):
            path.update(self.find_path_greedy_semirandom_bfs(0.84))

        all_possibe = [
            (i, j)
            for i in range(self._height)
            for j in range(self._width)
            if (i, j) not in path
            and self.at(i, j).state
            not in {
                CellState.CURRENT,
                CellState.GOAL,
                CellState.INACTIVE,
            }
        ]

        for i, j in all_possibe:
            self.at(i, j).change_state(CellState.INACTIVE)

    def at(self, row: int, col: int) -> Cell:
        return self._cells[col][row]

    def neighbors(self, row, col, *, shuffle: bool = True) -> list[tuple[int, int]]:
        ns = []
        for i, j in DIRECTIONS:
            new_i = row + i
            new_j = col + j
            if (
                (0 <= new_i < self._height)
                and (0 <= new_j < self._width)
                and (self.at(new_i, new_j).state != CellState.INACTIVE)
            ):
                ns.append((new_i, new_j))
        if shuffle:
            random.shuffle(ns)
        return ns

    def set_current(self, row: int, col: int) -> None:
        prev_current = self._current
        self._current = row, col
        self.at(row, col).make_current()
        if prev_current:
            self.at(*prev_current).revert_state()
            self.at(*prev_current).change_state(CellState.VISITED)

    def move_current(self, direction: tuple[int, int]) -> None:
        if not self._current:
            return
        direction_i, direction_j = direction
        if (
            (direction_i == -1 and self._current[0] == 0)
            or (direction_i == 1 and self._current[0] == (self._width - 1))
            or (direction_j == -1 and self._current[1] == 0)
            or (direction_j == 1 and self._current[1] == (self._height - 1))
        ):
            # invalid move, return
            return

        new_i, new_j = self._current[0] + direction_i, self._current[1] + direction_j
        self.set_current(new_i, new_j)

    def find_path_bfs(self) -> list[tuple[int, int]]:
        """finds a path from current to goal.
        returns the coordinates of the visited nodes."""

        # contains node, previous
        path: list[tuple[int, int]] = []
        visited = set()

        # queue
        to_visit = [self._current]

        while to_visit:
            current = to_visit.pop()

            # visit current
            path.append(current)

            if current == self._goal:
                # found the goal!
                return path

            # queue all neighbors
            for neighbor in self.neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    to_visit.insert(0, neighbor)

        return None  # didnt found a path to the goal

    def find_path_dfs(self, *, random_neighbor: bool = True) -> list[tuple[int, int]]:
        """finds a path from current to goal.
        returns the coordinates of the visited nodes."""

        path = []
        visited = set()

        # queue
        to_visit = [self._current]

        while to_visit:
            current = to_visit.pop()

            # visit current
            path.append(current)

            if current == self._goal:
                # found the goal!
                return path

            # queue all neighbors
            for neighbor in self.neighbors(*current, shuffle=random_neighbor):
                if neighbor not in visited:
                    visited.add(neighbor)
                    to_visit.append(neighbor)

        # visited all the accesible nodes, didnt found path :(
        return None  # didnt found a path to the goal

    def find_path_greedy_bfs(self) -> list[tuple[int, int]]:
        """finds a path from current to goal.
        returns the coordinates of the visited nodes."""

        # contains node, previous
        path: list[tuple[int, int]] = []
        visited = set()

        # queue
        to_visit = [
            PrioritizedNeighbor(
                manhattan_distance(self._current, self._goal),
                self._current,
            )
        ]

        while to_visit:
            current = heapq.heappop(to_visit).position

            # visit current
            path.append(current)

            if current == self._goal:
                # found the goal!
                return path

            # queue all neighbors
            for neighbor in self.neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    # keep to_visit sorted by manhattan distance to the goal
                    heapq.heappush(
                        to_visit,
                        PrioritizedNeighbor(
                            manhattan_distance(neighbor, self._goal),
                            neighbor,
                        ),
                    )
        return None  # didnt found a path to the goal

    def find_path_greedy_semirandom_bfs(
        self, random_ratio: float = 0.65
    ) -> list[tuple[int, int]]:
        """finds a path from current to goal.

        half greedy half random: when pickhing which node to visit next, sometimes pick a random one
        returns the coordinates of the visited nodes."""

        # contains node, previous
        path: list[tuple[int, int]] = []
        visited = set()

        # queue
        to_visit = [
            PrioritizedNeighbor(
                manhattan_distance(self._current, self._goal),
                self._current,
            )
        ]
        steps = 0
        while to_visit:
            steps += 1
            # if random.random() > random_ratio:
            if steps > 10:
                # use node with best heuristic
                current = heapq.heappop(to_visit).position
            else:
                # random node in the list to visit
                current = to_visit.pop(random.randrange(len(to_visit))).position
                # may have been de-heaped
                heapq.heapify(to_visit)

            # visit current
            path.append(current)

            if current == self._goal:
                # found the goal!
                return path

            # queue all neighbors
            for neighbor in self.neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    # keep to_visit sorted by manhattan distance to the goal
                    heapq.heappush(
                        to_visit,
                        PrioritizedNeighbor(
                            manhattan_distance(neighbor, self._goal),
                            neighbor,
                        ),
                    )
        return None  # didnt found a path to the goal

    def find_path_greedy_bfs(self) -> list[tuple[int, int]]:
        """finds a path from current to goal.
        returns the coordinates of the visited nodes."""

        # contains node, previous
        path: list[tuple[int, int]] = []
        visited = set()

        # queue
        to_visit = [
            PrioritizedNeighbor(
                manhattan_distance(self._current, self._goal),
                self._current,
            )
        ]

        while to_visit:
            current = heapq.heappop(to_visit).position

            # visit current
            path.append(current)

            if current == self._goal:
                # found the goal!
                return path

            # queue all neighbors
            for neighbor in self.neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    # keep to_visit sorted by manhattan distance to the goal
                    heapq.heappush(
                        to_visit,
                        PrioritizedNeighbor(
                            manhattan_distance(neighbor, self._goal),
                            neighbor,
                        ),
                    )
        return None  # didnt found a path to the goal

    def to_dict(self) -> dict:
        """Serialize the grid to a dictionary."""
        return {
            "width": self._width,
            "height": self._height,
            "cells": [[cell.state.name for cell in col] for col in self._cells],
            "current": self._current,
            "goal": self._goal,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Deserialize a grid from a dictionary."""
        grid = cls(
            width=data["width"],
            height=data["height"],
            initial_position=data.get("current"),
            goal_position=data.get("goal"),
        )
        for col_idx, col in enumerate(data["cells"]):
            for row_idx, state_name in enumerate(col):
                grid._cells[col_idx][row_idx].state = CellState[state_name]
        return grid
