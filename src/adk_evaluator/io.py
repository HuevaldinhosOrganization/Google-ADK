from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .models import GroundTruth, Prediction, Trajectory


def load_json(path: str) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: str, value: Any) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)


def load_ground_truths(path: str) -> List[GroundTruth]:
    payload = load_json(path)
    return [GroundTruth.from_dict(record) for record in payload]


def load_predictions(path: str) -> List[Prediction]:
    payload = load_json(path)
    return [Prediction.from_dict(record) for record in payload]


def serialize_results(results: Iterable[Any]) -> List[Dict[str, Any]]:
    return [result.to_dict() for result in results]
