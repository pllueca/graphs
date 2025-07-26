import argparse
import arcade
import random

# random.seed(42)

from lib.grid import GridGraph, CellState

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
}

BACKGROUND_COLOR = arcade.color.BLACK
UNKNOWN_COLOR = arcade.color.WHITE

# 4-way movement
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]


class MyGame(arcade.Window):
    """
    Main application class for drawing the grid.
    """

    def __init__(
        self,
        width: int,
        height: int,
        title: str,
        initial_position: tuple[int, int],
        goal_position: tuple[int, int],
        algorithm: str = "bfs",
        inactives: int = 300,
    ):
        super().__init__(width, height, title)
        arcade.set_background_color(BACKGROUND_COLOR)

        self.grid = GridGraph(
            GRID_COLS,
            GRID_ROWS,
            initial_position,
            goal_position,
            inactives=None,
        )

        if inactives > 0:
            self.grid.add_n_inactives(inactives)
        elif inactives < 0:
            self.grid.make_n_paths(abs(inactives))

        if algorithm == "bfs":
            self.path_to_goal = self.grid.find_path_bfs()
        elif algorithm == "dfs":
            self.path_to_goal = self.grid.find_path_dfs()
        elif algorithm == "greedy_bfs":
            self.path_to_goal = self.grid.find_path_greedy_bfs()
        elif algorithm == "greedy_random_bfs":
            self.path_to_goal = self.grid.find_path_greedy_semirandom_bfs()
        else:
            raise ValueError(f"algorithm {algorithm} not supported")

        self.step = 0
        if self.path_to_goal is not None:
            print(f"getting to goal is {len(self.path_to_goal)} steps")
            self.steps_to_goal = len(self.path_to_goal)
        else:
            print("no path to the goal")

    def on_draw(self):
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

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        if self.path_to_goal is None or self.step >= self.steps_to_goal:
            return

        self.grid.set_current(*self.path_to_goal[self.step])
        self.step += 1

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        self.click = True


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--initial", type=int, nargs=2, default=[1, 1])
    parser.add_argument("--algorithm", default="bfs")
    parser.add_argument("--inactives", type=int, default=100)
    return parser.parse_args()


def main():
    """Main function to set up and run the game."""
    args = parse_args()

    game = MyGame(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        SCREEN_TITLE,
        tuple(args.initial),
        (15, 25),
        algorithm=args.algorithm,
        inactives=args.inactives,
    )
    arcade.run()


if __name__ == "__main__":
    main()
