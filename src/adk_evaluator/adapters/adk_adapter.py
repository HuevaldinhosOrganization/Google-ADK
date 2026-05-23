from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ..models import GroundTruth, Prediction, TrajectoryPoint


AdkRecord = Dict[str, Any]


def load_adk_json(path: str) -> Any:
    """Load JSON data from an ADK format file.
    
    Args:
        path: File path to read JSON from.
    
    Returns:
        Parsed JSON data.
    """
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _extract_points(payload: AdkRecord) -> List[TrajectoryPoint]:
    """Extract trajectory points from ADK record with flexible field names.
    
    Supports multiple field naming conventions: 'points', 'steps', 'positions'.
    Supports coordinates in 'x'/'y' fields or nested 'location'/'position' objects.
    Supports time in 't', 'timestamp', or 'time' fields.
    
    Args:
        payload: ADK record dictionary.
    
    Returns:
        List of extracted TrajectoryPoint objects.
    """
    points: List[TrajectoryPoint] = []
    raw_points = payload.get("points") or payload.get("steps") or payload.get("positions")
    if raw_points is None:
        return points

    for raw in raw_points:
        x = raw.get("x")
        y = raw.get("y")
        t = raw.get("t") or raw.get("timestamp") or raw.get("time")
        if x is None or y is None:
            location = raw.get("location") or raw.get("position")
            if isinstance(location, dict):
                x = location.get("x")
                y = location.get("y")
        if x is None or y is None:
            continue
        points.append(TrajectoryPoint(x=float(x), y=float(y), t=None if t is None else float(t)))
    return points


def _parse_adk_record(payload: AdkRecord, record_type: str):
    """Parse an ADK record and convert to GroundTruth or Prediction.
    
    Extracts id, label, and points from flexible field names.
    Supports various id field names: 'id', 'trace_id', 'uuid'.
    Supports various label field names: 'label', 'type'.
    
    Args:
        payload: ADK record dictionary.
        record_type: Either 'ground_truth' or 'prediction'.
    
    Returns:
        GroundTruth or Prediction instance based on record_type.
    """
    return (
        GroundTruth(
            id=str(payload.get("id", payload.get("trace_id", payload.get("uuid", "")))),
            label=str(payload.get("label", payload.get("type", record_type))),
            points=tuple(_extract_points(payload)),
        )
        if record_type == "ground_truth"
        else Prediction(
            id=str(payload.get("id", payload.get("trace_id", payload.get("uuid", "")))),
            label=str(payload.get("label", payload.get("type", record_type))),
            points=tuple(_extract_points(payload)),
        )
    )


def load_adk_ground_truths(path: str) -> List[GroundTruth]:
    """Load ground truth trajectories from ADK format JSON file.
    
    Supports flexible JSON structure:
    - Direct array of records
    - Object with 'records' key
    - Object with 'ground_truths' key
    - Single record object
    
    Args:
        path: File path to ADK ground truth JSON.
    
    Returns:
        List of GroundTruth objects.
    """
    payload = load_adk_json(path)
    if isinstance(payload, dict):
        payload = payload.get("records", payload.get("ground_truths", [payload]))
    return [_parse_adk_record(record, "ground_truth") for record in payload]


def load_adk_predictions(path: str) -> List[Prediction]:
    """Load predicted trajectories from ADK format JSON file.
    
    Supports flexible JSON structure:
    - Direct array of records
    - Object with 'records' key
    - Object with 'predictions' key
    - Single record object
    
    Args:
        path: File path to ADK predictions JSON.
    
    Returns:
        List of Prediction objects.
    """
    payload = load_adk_json(path)
    if isinstance(payload, dict):
        payload = payload.get("records", payload.get("predictions", [payload]))
    return [_parse_adk_record(record, "prediction") for record in payload]
