import json
from pathlib import Path

from adk_evaluator.io import load_ground_truths, load_predictions, save_json
from adk_evaluator.models import GroundTruth, Prediction


def test_json_io_roundtrip(tmp_path: Path):
    ground_truths = [
        GroundTruth(
            id="route-1",
            label="survey",
            points=[],
        )
    ]
    predictions = [
        Prediction(
            id="route-1",
            label="survey",
            points=[],
        )
    ]

    ground_truth_file = tmp_path / "ground_truth.json"
    predictions_file = tmp_path / "predictions.json"
    output_file = tmp_path / "output.json"

    save_json(ground_truth_file.as_posix(), [truth.to_dict() for truth in ground_truths])
    save_json(predictions_file.as_posix(), [prediction.to_dict() for prediction in predictions])

    loaded_truths = load_ground_truths(ground_truth_file.as_posix())
    loaded_predictions = load_predictions(predictions_file.as_posix())

    assert len(loaded_truths) == 1
    assert isinstance(loaded_truths[0], GroundTruth)
    assert len(loaded_predictions) == 1
    assert isinstance(loaded_predictions[0], Prediction)

    save_json(output_file.as_posix(), [{"ok": True}])
    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert data == [{"ok": True}]
