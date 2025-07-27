import argparse
import arcade
import random
from pathlib import Path
from enum import Enum, auto

# random.seed(42)

from lib.grid import GridGraph, CellState
from lib.persistence import save_grid_to_json, load_grid_from_json

# --- Grid and Cell Constants ---
GRID_ROWS = 20  # Number of rows (N)
GRID_COLS = 30  # Number of columns (M)

CELL_SIZE = 25  # Width and height of each cell in pixels
MARGIN = 5  # Margin between cells in pixels

# --- Screen Constants ---
# Calculate screen dimensions based on the grid
SCREEN_WIDTH = (CELL_SIZE + MARGIN) * GRID_COLS + MARGIN
SCREEN_HEIGHT = (CELL_SIZE + MARGIN) * GRID_ROWS + MARGIN
SCREEN_TITLE = "grid search algorithms."

# --- Color Constants ---
CELL_STATE_TO_COLOR = {
    CellState.ACTIVE: arcade.color.GREEN,
    CellState.INACTIVE: arcade.color.RED,
    CellState.CURRENT: arcade.color.BLUE,
    CellState.VISITED: arcade.color.DARK_BLUE,
    CellState.GOAL: arcade.color.YELLOW,
    CellState.SLOW: arcade.color.PURPLE,
}

BACKGROUND_COLOR = arcade.color.BLACK
UNKNOWN_COLOR = arcade.color.WHITE

# 4-way movement
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

AUTOSTEP_EVERY : float = 0.25


class GameMode(Enum):
    SEARCH = auto()
    EDIT = auto()


class MyGame(arcade.Window):
    """
    Main application class for drawing the grid.
    """

    grid          : GridGraph
    game_mode     : GameMode
    algorithm     : str
    cells_changed : bool

    autoplay        : bool
    should_step     : bool
    time_since_step : float

    def __init__(
        self,
        width: int,
        height: int,
        title: str,
        grid: GridGraph,
        algorithm: str = "bfs",
    ):
        super().__init__(width, height, title)
        arcade.set_background_color(BACKGROUND_COLOR)

        self.grid          = grid
        self.game_mode     = GameMode.SEARCH
        self.algorithm     = algorithm
        self.cells_changed = False

        self.autoplay        = False
        self.should_step     = False
        self.time_since_step = 0.0

        self.compute_path()

    def compute_path(self) -> None:
        match self.algorithm:
            case "bfs":
                self.path_to_goal = self.grid.find_path_bfs()
            case "dfs":
                self.path_to_goal = self.grid.find_path_dfs()
            case "greedy_bfs":
                self.path_to_goal = self.grid.find_path_greedy_bfs()
            case "greedy_random_bfs":
                self.path_to_goal = self.grid.find_path_greedy_semirandom_bfs()
            case _:
                raise ValueError(f"algorithm {self.algorithm} not supported")

        self.step = 0
        if self.path_to_goal is not None:
            self.steps_to_goal = len(self.path_to_goal)
            self.path_cost = self.grid.path_cost(self.path_to_goal)
            print(
                f"getting to goal is {len(self.path_to_goal)} steps, cost: {self.path_cost}"
            )
        else:
            print("no path to the goal")

    def on_draw(self) -> None:
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        self.clear()

        # Loop through each grid location
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                # Determine the color based on the state (1 or 0)
                cell = self.grid.at(row, col)
                color = CELL_STATE_TO_COLOR.get(cell.state, UNKNOWN_COLOR)

                # Calculate the center x, y coordinates for the rectangle
                x = (MARGIN + CELL_SIZE) * col + MARGIN + CELL_SIZE // 2
                y = (MARGIN + CELL_SIZE) * row + MARGIN + CELL_SIZE // 2

                arcade.draw_rect_outline(
                    arcade.rect.XYWH(x, y, CELL_SIZE, CELL_SIZE),
                    color,
                )

    def on_update(self, delta_time: float) -> None:
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        if self.game_mode == GameMode.SEARCH:
            self.time_since_step += delta_time

            if self.autoplay and self.time_since_step > AUTOSTEP_EVERY:
                self.should_step = True

            if self.should_step:
                if self.path_to_goal is None or self.step >= self.steps_to_goal:
                    return
                self.grid.set_current(*self.path_to_goal[self.step])
                self.step += 1
                self.time_since_step = 0.0

            self.should_step = False

    def on_key_press(self, key, key_modifiers) -> None:
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        match key:
            case arcade.key.ESCAPE:
                arcade.close_window()

            case arcade.key.E:
                self.game_mode = GameMode.EDIT
                self.cells_changed = False

            case arcade.key.S:
                self.game_mode = GameMode.SEARCH
                if self.cells_changed:
                    self.compute_path()

            case arcade.key.SPACE:
                if self.game_mode == GameMode.SEARCH:
                    self.should_step = True

            case arcade.key.P:
                self.autoplay = not self.autoplay

    def on_mouse_press(self, x, y, button, key_modifiers) -> None:
        """
        If in search mode, advance a step. if in edit mode, flip the current tile from active to inactive.
        """
        match self.game_mode:
            case GameMode.SEARCH:
                self.should_step = True

            case GameMode.EDIT:
                grid_tile_i, grid_tile_j = self.mouse_position_to_tile(x, y)
                self.grid.at(grid_tile_i, grid_tile_j).flip_active()
                self.cells_changed = True

    def mouse_position_to_tile(self, x, y) -> tuple[int, int]:
        col = (x - MARGIN) // (CELL_SIZE + MARGIN)
        row = (y - MARGIN) // (CELL_SIZE + MARGIN)
        return int(row), int(col)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--initial", type=int, nargs=2, default=[1, 1])
    parser.add_argument("--algorithm", default="bfs")
    parser.add_argument("--inactives", type=int, default=100)
    parser.add_argument(
        "--load",
        type=str,
        default=None,
        help="Path to grid JSON file",
    )
    parser.add_argument(
        "--save",
        type=str,
        default=None,
        help="If not None, path to save grid JSON file",
    )
    return parser.parse_args()


def main() -> None:
    """Main function to set up and run the game."""
    args = parse_args()

    if args.load is not None:
        grid = load_grid_from_json(args.load)
    else:
        goal_position = 15, 25
        initial_position = tuple(args.initial)
        inactives = args.inactives
        grid = GridGraph(
            GRID_COLS,
            GRID_ROWS,
            initial_position=initial_position,
            goal_position=goal_position,
        )

        if inactives > 0:
            grid.add_n_inactives(inactives)
        elif inactives < 0:
            grid.make_n_paths(abs(inactives))

    if args.save is not None:
        psave = Path(args.save)
        if psave.exists():
            raise FileExistsError(f"File {psave} already exists.")
        elif not psave.parent.exists():
            raise FileNotFoundError(f"Parent directory {psave.parent} does not exist.")
        save_grid_to_json(grid, str(psave))

    game = MyGame(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        SCREEN_TITLE,
        grid=grid,
        algorithm=args.algorithm,
    )
    arcade.run()


if __name__ == "__main__":
    main()
