from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, Sequence
import math

from .models import EvaluationResult, GroundTruth, Prediction, TrajectoryPoint


class Evaluator(ABC):
    @abstractmethod
    def evaluate(self, truth: GroundTruth, prediction: Prediction) -> EvaluationResult:
        raise NotImplementedError


class TrajectoryEvaluator(Evaluator):
    def __init__(
        self,
        coverage_tolerance: float = 1.0,
        match_by_id_first: bool = True,
    ) -> None:
        self.coverage_tolerance = coverage_tolerance
        self.match_by_id_first = match_by_id_first

    def evaluate(self, truth: GroundTruth, prediction: Prediction) -> EvaluationResult:
        path_error = self._average_point_distance(truth.points, prediction.points)
        coverage = self._coverage(truth.points, prediction.points)
        duration_error = self._duration_error(truth.points, prediction.points)
        label_match = truth.label == prediction.label
        return EvaluationResult(
            trajectory_id=prediction.id,
            matched_truth_id=truth.id,
            path_error=path_error,
            coverage=coverage,
            duration_error=duration_error,
            label_match=label_match,
        )

    def evaluate_batch(
        self, truths: Iterable[GroundTruth], predictions: Iterable[Prediction]
    ) -> List[EvaluationResult]:
        truth_list = list(truths)
        truth_index = {truth.id: truth for truth in truth_list}
        results: List[EvaluationResult] = []

        for prediction in predictions:
            truth = self._match_truth(prediction, truth_list, truth_index)
            if truth is None:
                continue
            results.append(self.evaluate(truth, prediction))

        return results

    def _match_truth(
        self,
        prediction: Prediction,
        truth_list: Sequence[GroundTruth],
        truth_index: dict[str, GroundTruth],
    ) -> Optional[GroundTruth]:
        if self.match_by_id_first and prediction.id in truth_index:
            return truth_index[prediction.id]

        if not truth_list:
            return None

        best_truth = min(
            truth_list,
            key=lambda truth: self._average_point_distance(truth.points, prediction.points),
        )
        return best_truth

    def _average_point_distance(
        self,
        truth_points: tuple[TrajectoryPoint, ...],
        prediction_points: tuple[TrajectoryPoint, ...],
    ) -> float:
        if not truth_points and not prediction_points:
            return 0.0
        if not truth_points or not prediction_points:
            return float("inf")

        count = min(len(truth_points), len(prediction_points))
        total_distance = sum(
            truth_points[index].distance_to(prediction_points[index])
            for index in range(count)
        )
        return total_distance / count

    def _coverage(
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

    def _duration_error(
        self,
        truth_points: tuple[TrajectoryPoint, ...],
        prediction_points: tuple[TrajectoryPoint, ...],
    ) -> Optional[float]:
        if not truth_points or not prediction_points:
            return None

        truth_times = [point.t for point in truth_points if point.t is not None]
        pred_times = [point.t for point in prediction_points if point.t is not None]
        if not truth_times or not pred_times:
            return None

        return abs(truth_times[-1] - pred_times[-1])
