from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .evaluation import TrajectoryEvaluator
from .models import EvaluationResult, GroundTruth, Prediction, TrajectoryPoint


@dataclass(frozen=True)
class AdkEvaluationResult(EvaluationResult):
    """Evaluation result with ADK-specific metrics (precision, recall, F1, ADK score)."""
    precision: float
    recall: float
    f1_score: float
    adk_score: float

    def to_dict(self) -> dict:
        """Convert to dictionary including ADK metrics.
        
        Returns:
            Dictionary with all evaluation and ADK metrics.
        """
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
    """Evaluator that computes ADK-specific metrics including precision, recall, and F1 score."""
    def evaluate(self, truth: GroundTruth, prediction: Prediction) -> AdkEvaluationResult:
        """Evaluate prediction with ADK metrics (precision, recall, F1, ADK score).
        
        Extends base evaluation with precision (coverage), recall (truth coverage),
        F1 score, and composite ADK score combining path error, F1, and duration.
        
        Args:
            truth: Ground truth trajectory.
            prediction: Predicted trajectory.
        
        Returns:
            AdkEvaluationResult with all metrics.
        """
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
        """Calculate fraction of ground truth points covered by predictions (recall).
        
        Args:
            truth_points: Ground truth trajectory points.
            prediction_points: Predicted trajectory points.
        
        Returns:
            Recall ratio (0.0 to 1.0).
        """
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
        """Calculate F1 score from precision and recall.
        
        Args:
            precision: Precision metric (0.0 to 1.0).
            recall: Recall metric (0.0 to 1.0).
        
        Returns:
            F1 score (0.0 to 1.0).
        """
        if precision + recall == 0.0:
            return 0.0
        return 2.0 * precision * recall / (precision + recall)

    def _adk_score(
        self, path_error: float, f1_score: float, duration_error: Optional[float]
    ) -> float:
        """Calculate composite ADK score from F1, path error, and duration error.
        
        Score = F1 * (1 / (1 + path_error)) * (1 / (1 + |duration_error| / 60))
        where penalties are applied for path and duration deviations.
        
        Args:
            path_error: Average point distance error.
            f1_score: F1 score (0.0 to 1.0).
            duration_error: Absolute duration difference in seconds, or None.
        
        Returns:
            Composite ADK score.
        """
        if f1_score == 0.0:
            return 0.0

        error_penalty = 1.0 / (1.0 + path_error)
        duration_penalty = 1.0
        if duration_error is not None:
            duration_penalty = 1.0 / (1.0 + abs(duration_error) / 60.0)

        return round(f1_score * error_penalty * duration_penalty, 4)
