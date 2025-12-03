"""Shared file operations for agents."""
import json
import os
from pathlib import Path
from typing import Any

# Base data directory
DATA_DIR = Path(__file__).parent.parent / "shared" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_json(filename: str, data: Any) -> bool:
    """Save data to a JSON file in the shared data directory."""
    try:
        filepath = DATA_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False


def load_json(filename: str, default: Any = None) -> Any:
    """Load data from a JSON file in the shared data directory."""
    try:
        filepath = DATA_DIR / filename
        if not filepath.exists():
            return default if default is not None else {}
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return default if default is not None else {}


def append_json(filename: str, item: Any) -> bool:
    """Append an item to a JSON array file."""
    try:
        filepath = DATA_DIR / filename
        data = load_json(filename, default=[])
        if not isinstance(data, list):
            data = []
        data.append(item)
        return save_json(filename, data)
    except Exception as e:
        print(f"Error appending to {filename}: {e}")
        return False


