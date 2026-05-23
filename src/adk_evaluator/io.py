from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .models import GroundTruth, Prediction, Trajectory


def load_json(path: str) -> Any:
    """Load JSON data from a file.
    
    Args:
        path: File path to read JSON from.
    
    Returns:
        Parsed JSON data.
    """
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: str, value: Any) -> None:
    """Save data to a JSON file, creating parent directories as needed.
    
    Args:
        path: File path to write JSON to.
        value: Data to serialize to JSON.
    """
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)


def load_ground_truths(path: str) -> List[GroundTruth]:
    """Load ground truth trajectories from a JSON file.
    
    Args:
        path: File path containing ground truth JSON data.
    
    Returns:
        List of GroundTruth objects.
    """
    payload = load_json(path)
    return [GroundTruth.from_dict(record) for record in payload]


def load_predictions(path: str) -> List[Prediction]:
    """Load predicted trajectories from a JSON file.
    
    Args:
        path: File path containing prediction JSON data.
    
    Returns:
        List of Prediction objects.
    """
    payload = load_json(path)
    return [Prediction.from_dict(record) for record in payload]


def serialize_results(results: Iterable[Any]) -> List[Dict[str, Any]]:
    """Convert evaluation results to dictionaries for JSON serialization.
    
    Args:
        results: Iterable of evaluation result objects.
    
    Returns:
        List of dictionaries representing the results.
    """
    return [result.to_dict() for result in results]
