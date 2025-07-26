from dataclasses import dataclass, field
from enum import Enum, auto
import random
import heapq

from .distance_utils import manhattan_distance


class CellState(Enum):
    ACTIVE = auto()
    INACTIVE = auto()
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

    def revert_current(self):
        if self.state != CellState.CURRENT:
            raise Exception("should be current")
        if not self.prev_state:
            raise Exception("no prev state")
        self.state = self.prev_state

    def make_goal(self):
        self.prev_state = self.state
        self.state = CellState.GOAL

    def revert_goal(self):
        if self.state != CellState.GOAL:
            raise Exception("should be goal")
        if not self.prev_state:
            raise Exception("no prev state")
        self.state = self.prev_state


class GridGraph:

    def __init__(
        self,
        width: int,
        height: int,
        initial_position: tuple[int, int] | None = None,
        goal_position: tuple[int, int] | None = None,
        inactives: None | int | list[tuple[int, int]] = None,
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
            if isinstance(inactives, int):
                inactives_list = []
                while len(inactives_list) < inactives:
                    i = random.randint(0, self._height - 1)
                    j = random.randint(0, self._width - 1)
                    if self.at(i, j).state not in {CellState.CURRENT, CellState.GOAL}:
                        inactives_list.append((i, j))
                inactives = inactives_list
            if isinstance(inactives, list):
                # list of positions to mark as inactive
                for i, j in inactives:
                    self.at(i, j).change_state(CellState.INACTIVE)

    def add_n_inactives(self, n: int):
        """Adds n inactive squares to the map, ensuring that there is always at least 1 path from initial to goal"""
        path = set(self.find_path_dfs(random_neighbor=True))
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

        @dataclass(order=True)
        class PrioritizedNeighbor:
            distance: int
            position: tuple[int, int]

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
