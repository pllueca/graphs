import json
from .grid import GridGraph


def save_grid_to_json(g: GridGraph, filepath: str):
    """Save the grid to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(g.to_dict(), f)


def load_grid_from_json(filepath: str) -> GridGraph:
    """Load the grid from a JSON file."""
    with open(filepath, "r") as f:
        data = json.load(f)
    return GridGraph.from_dict(data)
