from __future__ import annotations

from typing import Iterable, List

from .evaluation import TrajectoryEvaluator
from .io import load_ground_truths, load_predictions, save_json, serialize_results
from .models import GroundTruth, Prediction, EvaluationResult


class EvaluationService:
    def __init__(self, evaluator: TrajectoryEvaluator | None = None) -> None:
        self.evaluator = evaluator or TrajectoryEvaluator()

    def evaluate(
        self, truths: Iterable[GroundTruth], predictions: Iterable[Prediction]
    ) -> List[EvaluationResult]:
        return self.evaluator.evaluate_batch(truths, predictions)

    def evaluate_files(
        self,
        ground_truth_path: str,
        prediction_path: str,
        output_path: str,
        coverage_tolerance: float = 1.0,
    ) -> List[EvaluationResult]:
        truths = load_ground_truths(ground_truth_path)
        predictions = load_predictions(prediction_path)
        self.evaluator = TrajectoryEvaluator(coverage_tolerance=coverage_tolerance)
        results = self.evaluate(truths, predictions)
        save_json(output_path, serialize_results(results))
        return results
