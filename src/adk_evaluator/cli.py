from __future__ import annotations

import argparse
import sys

from .service import EvaluationService


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the evaluation tool.
    
    Args:
        argv: List of command-line arguments. If None, uses sys.argv.
    
    Returns:
        Parsed command-line arguments with ground_truth, predictions, output,
        coverage_tolerance, report_type, and input_format attributes.
    """
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
    parser.add_argument(
        "--report-type",
        choices=["standard", "adk"],
        default="standard",
        help="Choose the evaluation report type: standard or adk.",
    )
    parser.add_argument(
        "--input-format",
        choices=["standard", "adk"],
        default="standard",
        help="Choose the input data format: standard JSON or ADK JSON.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the evaluation CLI.
    
    Parses arguments, creates an EvaluationService, and evaluates prediction files
    against ground truth files, writing results to the specified output path.
    
    Args:
        argv: List of command-line arguments. If None, uses sys.argv.
    
    Returns:
        Exit code (0 for success).
    """
    args = parse_args(argv)
    service = EvaluationService(
        report_type=args.report_type,
        coverage_tolerance=args.coverage_tolerance,
        input_format=args.input_format,
    )
    results = service.evaluate_files(
        ground_truth_path=args.ground_truth,
        prediction_path=args.predictions,
        output_path=args.output,
        coverage_tolerance=args.coverage_tolerance,
        report_type=args.report_type,
        input_format=args.input_format,
    )

    print(f"Evaluated {len(results)} matched trajectories.")
    print(f"Results written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
