from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple
import math

PointType = Dict[str, float]

@dataclass(frozen=True)
class TrajectoryPoint:
    x: float
    y: float
    t: Optional[float] = None

    def to_dict(self) -> PointType:
        """Convert trajectory point to dictionary.
        
        Returns:
            Dictionary with x, y coordinates and optional time t.
        """
        payload: PointType = {"x": self.x, "y": self.y}
        if self.t is not None:
            payload["t"] = self.t
        return payload

    @staticmethod
    def from_dict(payload: PointType) -> "TrajectoryPoint":
        """Create a TrajectoryPoint from a dictionary.
        
        Args:
            payload: Dictionary containing x, y, and optional t keys.
        
        Returns:
            TrajectoryPoint instance.
        """
        return TrajectoryPoint(
            x=float(payload.get("x", 0.0)),
            y=float(payload.get("y", 0.0)),
            t=None if payload.get("t") is None else float(payload.get("t")),
        )

    def distance_to(self, other: "TrajectoryPoint") -> float:
        """Calculate Euclidean distance to another point.
        
        Args:
            other: Another TrajectoryPoint.
        
        Returns:
            Euclidean distance between the two points.
        """
        return math.hypot(self.x - other.x, self.y - other.y)


@dataclass(frozen=True)
class Trajectory:
    id: str
    label: str
    points: Tuple[TrajectoryPoint, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Trajectory":
        """Create a Trajectory from a dictionary.
        
        Args:
            payload: Dictionary with id, label, and points list.
        
        Returns:
            Trajectory instance.
        """
        raw_points = payload.get("points", [])
        points = tuple(TrajectoryPoint.from_dict(point) for point in raw_points)
        return cls(
            id=str(payload.get("id", "")),
            label=str(payload.get("label", "")),
            points=points,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert trajectory to dictionary.
        
        Returns:
            Dictionary with id, label, and points list.
        """
        return {
            "id": self.id,
            "label": self.label,
            "points": [point.to_dict() for point in self.points],
        }

    @property
    def point_count(self) -> int:
        """Get the number of points in the trajectory.
        
        Returns:
            Number of trajectory points.
        """
        return len(self.points)

    @property
    def length(self) -> float:
        """Calculate total trajectory length as sum of distances between consecutive points.
        
        Returns:
            Total distance traveled along the trajectory.
        """
        if self.point_count < 2:
            return 0.0
        return sum(
            self.points[index].distance_to(self.points[index + 1])
            for index in range(self.point_count - 1)
        )


@dataclass(frozen=True)
class GroundTruth(Trajectory):
    pass


@dataclass(frozen=True)
class Prediction(Trajectory):
    pass


@dataclass(frozen=True)
class EvaluationResult:
    trajectory_id: str
    path_error: float
    coverage: float
    duration_error: Optional[float]
    label_match: bool
    matched_truth_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert evaluation result to dictionary.
        
        Returns:
            Dictionary with all evaluation metrics.
        """
        payload = {
            "trajectory_id": self.trajectory_id,
            "matched_truth_id": self.matched_truth_id,
            "path_error": self.path_error,
            "coverage": self.coverage,
            "label_match": self.label_match,
        }
        if self.duration_error is not None:
            payload["duration_error"] = self.duration_error
        return payload
