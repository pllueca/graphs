import json
from pathlib import Path
import uuid
from .grid import GridGraph


def save_grid_to_json(g: GridGraph, filepath: str | Path | None = None):
    """Save the grid to a JSON file."""
    if filepath is None:
        filepath = Path(f"map_{uuid.uuid4()}.json")
    elif isinstance(filepath, str):
        filepath = Path(filepath)
    if filepath.exists():
        raise FileExistsError(f"File {filepath} already exists.")
    elif not filepath.parent.exists():
        raise FileNotFoundError(f"Parent directory {filepath.parent} does not exist.")
    with filepath.open("w") as f:
        json.dump(g.to_dict(), f)

    print(f"saved grid to {filepath}")


def load_grid_from_json(filepath: str) -> GridGraph:
    """Load the grid from a JSON file."""
    with open(filepath, "r") as f:
        data = json.load(f)
    return GridGraph.from_dict(data)
