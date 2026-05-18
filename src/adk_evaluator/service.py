from __future__ import annotations

from typing import Iterable, List

from .adk_evaluation import AdkTrajectoryEvaluator
from .adapters.adk_adapter import load_adk_ground_truths, load_adk_predictions
from .evaluation import TrajectoryEvaluator
from .io import load_ground_truths, load_predictions, save_json, serialize_results
from .models import GroundTruth, Prediction, EvaluationResult


class EvaluationService:
    def __init__(
        self,
        evaluator: TrajectoryEvaluator | None = None,
        report_type: str = "standard",
        coverage_tolerance: float = 1.0,
        input_format: str = "standard",
    ) -> None:
        self.report_type = report_type
        self.coverage_tolerance = coverage_tolerance
        self.input_format = input_format
        self.evaluator = evaluator or self._build_evaluator()

    def _build_evaluator(self) -> TrajectoryEvaluator:
        if self.report_type == "adk":
            return AdkTrajectoryEvaluator(coverage_tolerance=self.coverage_tolerance)
        return TrajectoryEvaluator(coverage_tolerance=self.coverage_tolerance)

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
        report_type: str = "standard",
        input_format: str = "standard",
    ) -> List[EvaluationResult]:
        self.report_type = report_type
        self.coverage_tolerance = coverage_tolerance
        self.input_format = input_format
        self.evaluator = self._build_evaluator()

        if self.input_format == "adk":
            truths = load_adk_ground_truths(ground_truth_path)
            predictions = load_adk_predictions(prediction_path)
        else:
            truths = load_ground_truths(ground_truth_path)
            predictions = load_predictions(prediction_path)

        results = self.evaluate(truths, predictions)
        save_json(output_path, serialize_results(results))
        return results
