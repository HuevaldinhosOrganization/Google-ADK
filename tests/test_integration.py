from pathlib import Path

from adk_evaluator.service import EvaluationService


def test_integration_evaluation_with_complex_dataset(tmp_path: Path):
    """Test end-to-end evaluation pipeline with complex dataset.
    
    Verifies:
    - Complex trajectories with multiple points are loaded correctly
    - EvaluationService processes ground truths and predictions
    - Results are written to output file
    - All expected metrics are present in results (trajectory_id, coverage, matched_truth_id, label_match, duration_error)
    - Some trajectories match labels and some have duration errors
    """
    source_ground_truth = Path("data/sample_ground_truth_complex.json")
    source_predictions = Path("data/sample_predictions_complex.json")
    output_file = tmp_path / "evaluation_results.json"

    assert source_ground_truth.exists()
    assert source_predictions.exists()

    service = EvaluationService()
    results = service.evaluate_files(
        ground_truth_path=str(source_ground_truth),
        prediction_path=str(source_predictions),
        output_path=str(output_file),
        coverage_tolerance=1.0,
    )

    assert len(results) == 4
    assert output_file.exists()

    result_dicts = [result.to_dict() for result in results]
    assert all("trajectory_id" in record for record in result_dicts)
    assert all("coverage" in record for record in result_dicts)
    assert all("matched_truth_id" in record for record in result_dicts)
    assert any(record["label_match"] for record in result_dicts)
    assert any(record.get("duration_error") is not None for record in result_dicts)
