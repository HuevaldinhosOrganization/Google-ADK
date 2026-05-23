import json
from pathlib import Path

from adk_evaluator.adapters.adk_adapter import load_adk_ground_truths, load_adk_predictions
from adk_evaluator.service import EvaluationService


def test_adk_adapter_loads_adk_records(tmp_path: Path):
    """Test that ADK adapter correctly loads and parses ADK format JSON.
    
    Verifies:
    - Ground truths are loaded from ADK records with nested location fields
    - Predictions are loaded from ADK records
    - Flexible field names (trace_id, type, steps) are handled
    - Point extraction works with nested location objects
    """
    ground_truth_file = tmp_path / "adk_ground_truth.json"
    prediction_file = tmp_path / "adk_predictions.json"

    ground_truth_file.write_text(
        json.dumps(
            {
                "records": [
                    {
                        "trace_id": "agent-1",
                        "type": "mission",
                        "steps": [
                            {"location": {"x": 0.0, "y": 0.0}, "timestamp": 0},
                            {"location": {"x": 1.0, "y": 1.0}, "timestamp": 30},
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    prediction_file.write_text(
        json.dumps(
            {
                "records": [
                    {
                        "trace_id": "agent-1",
                        "type": "mission",
                        "steps": [
                            {"location": {"x": 0.1, "y": 0.1}, "timestamp": 0},
                            {"location": {"x": 1.1, "y": 1.1}, "timestamp": 31},
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    truths = load_adk_ground_truths(str(ground_truth_file))
    predictions = load_adk_predictions(str(prediction_file))

    assert len(truths) == 1
    assert len(predictions) == 1
    assert truths[0].id == "agent-1"
    assert predictions[0].id == "agent-1"
    assert truths[0].label == "mission"
    assert predictions[0].label == "mission"
    assert truths[0].point_count == 2
    assert predictions[0].point_count == 2


def test_adk_service_uses_adk_input_format(tmp_path: Path):
    """Test that EvaluationService correctly evaluates using ADK input format and report type.
    
    Verifies:
    - ADK format input loading with flexible field names (id, label, steps)
    - ADK report type generates results with ADK-specific metrics
    - Precision, recall, F1, and adk_score are computed correctly
    """
    ground_truth_file = tmp_path / "adk_ground_truth.json"
    prediction_file = tmp_path / "adk_predictions.json"
    output_file = tmp_path / "adk_results.json"

    ground_truth_file.write_text(
        json.dumps(
            {
                "records": [
                    {
                        "id": "route-1",
                        "label": "delivery",
                        "steps": [
                            {"x": 0.0, "y": 0.0, "t": 0},
                            {"x": 1.0, "y": 1.0, "t": 30},
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    prediction_file.write_text(
        json.dumps(
            {
                "records": [
                    {
                        "id": "route-1",
                        "label": "delivery",
                        "steps": [
                            {"x": 0.1, "y": 0.1, "t": 0},
                            {"x": 1.1, "y": 1.1, "t": 32},
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    service = EvaluationService(report_type="adk", input_format="adk")
    results = service.evaluate_files(
        ground_truth_path=str(ground_truth_file),
        prediction_path=str(prediction_file),
        output_path=str(output_file),
        coverage_tolerance=0.5,
        report_type="adk",
        input_format="adk",
    )

    assert output_file.exists()
    assert len(results) == 1
    result_dict = results[0].to_dict()
    assert result_dict["precision"] == 1.0
    assert result_dict["recall"] == 1.0
    assert result_dict["f1_score"] == 1.0
    assert "adk_score" in result_dict
