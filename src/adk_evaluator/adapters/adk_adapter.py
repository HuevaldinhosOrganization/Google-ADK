from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ..models import GroundTruth, Prediction, TrajectoryPoint


AdkRecord = Dict[str, Any]


def load_adk_json(path: str) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _extract_points(payload: AdkRecord) -> List[TrajectoryPoint]:
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
    payload = load_adk_json(path)
    if isinstance(payload, dict):
        payload = payload.get("records", payload.get("ground_truths", [payload]))
    return [_parse_adk_record(record, "ground_truth") for record in payload]


def load_adk_predictions(path: str) -> List[Prediction]:
    payload = load_adk_json(path)
    if isinstance(payload, dict):
        payload = payload.get("records", payload.get("predictions", [payload]))
    return [_parse_adk_record(record, "prediction") for record in payload]
