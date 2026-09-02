"""
I/O and YAML/JSON serialization utilities for CryptoTrace AI.
"""

import os
import yaml
import json
import joblib
from typing import Any, Dict


def load_yaml(filepath: str) -> Dict[str, Any]:
    """Load and parse YAML configuration file."""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_json(data: Any, filepath: str, indent: int = 2):
    """Save Python data structure to JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)


def load_json(filepath: str) -> Any:
    """Load JSON file."""
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
