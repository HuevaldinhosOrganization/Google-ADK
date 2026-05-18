from __future__ import annotations

import argparse
import sys

from .service import EvaluationService


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate predictions against ground truth trajectories."
    )
    parser.add_argument(
        "--ground-truth",
        required=True,
        help="Path to the ground truth JSON file.",
    )
    parser.add_argument(
        "--predictions",
        required=True,
        help="Path to the predictions JSON file.",
    )
    parser.add_argument(
        "--output",
        default="results.json",
        help="Path for the evaluation results JSON output.",
    )
    parser.add_argument(
        "--coverage-tolerance",
        type=float,
        default=1.0,
        help="Maximum distance for coverage between predicted and truth points.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    service = EvaluationService()
    results = service.evaluate_files(
        ground_truth_path=args.ground_truth,
        prediction_path=args.predictions,
        output_path=args.output,
        coverage_tolerance=args.coverage_tolerance,
    )

    print(f"Evaluated {len(results)} matched trajectories.")
    print(f"Results written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
