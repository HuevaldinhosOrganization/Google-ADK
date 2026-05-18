from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .evaluation import TrajectoryEvaluator
from .models import EvaluationResult, GroundTruth, Prediction, TrajectoryPoint


@dataclass(frozen=True)
class AdkEvaluationResult(EvaluationResult):
    precision: float
    recall: float
    f1_score: float
    adk_score: float

    def to_dict(self) -> dict:
        payload = super().to_dict()
        payload.update(
            {
                "precision": self.precision,
                "recall": self.recall,
                "f1_score": self.f1_score,
                "adk_score": self.adk_score,
            }
        )
        return payload


class AdkTrajectoryEvaluator(TrajectoryEvaluator):
    def evaluate(self, truth: GroundTruth, prediction: Prediction) -> AdkEvaluationResult:
        base = super().evaluate(truth, prediction)
        precision = self._coverage(truth.points, prediction.points)
        recall = self._truth_coverage(truth.points, prediction.points)
        f1_score = self._f1(precision, recall)
        adk_score = self._adk_score(base.path_error, f1_score, base.duration_error)
        return AdkEvaluationResult(
            trajectory_id=base.trajectory_id,
            matched_truth_id=base.matched_truth_id,
            path_error=base.path_error,
            coverage=base.coverage,
            duration_error=base.duration_error,
            label_match=base.label_match,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            adk_score=adk_score,
        )

    def _truth_coverage(
        self,
        truth_points: tuple[TrajectoryPoint, ...],
        prediction_points: tuple[TrajectoryPoint, ...],
    ) -> float:
        if not truth_points or not prediction_points:
            return 0.0

        covered_truth = 0
        for truth_point in truth_points:
            if any(
                truth_point.distance_to(prediction_point) <= self.coverage_tolerance
                for prediction_point in prediction_points
            ):
                covered_truth += 1
        return covered_truth / len(truth_points)

    def _f1(self, precision: float, recall: float) -> float:
        if precision + recall == 0.0:
            return 0.0
        return 2.0 * precision * recall / (precision + recall)

    def _adk_score(
        self, path_error: float, f1_score: float, duration_error: Optional[float]
    ) -> float:
        if f1_score == 0.0:
            return 0.0

        error_penalty = 1.0 / (1.0 + path_error)
        duration_penalty = 1.0
        if duration_error is not None:
            duration_penalty = 1.0 / (1.0 + abs(duration_error) / 60.0)

        return round(f1_score * error_penalty * duration_penalty, 4)
