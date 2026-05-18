from adk_evaluator.evaluation import TrajectoryEvaluator
from adk_evaluator.models import GroundTruth, Prediction, TrajectoryPoint


def test_trajectory_evaluator_reports_metrics():
    truth = GroundTruth(
        id="route-1",
        label="delivery",
        points=(
            TrajectoryPoint(x=0.0, y=0.0, t=0.0),
            TrajectoryPoint(x=1.0, y=1.0, t=60.0),
        ),
    )
    prediction = Prediction(
        id="route-1",
        label="delivery",
        points=(
            TrajectoryPoint(x=0.1, y=0.1, t=0.0),
            TrajectoryPoint(x=1.1, y=1.1, t=60.0),
        ),
    )

    evaluator = TrajectoryEvaluator(coverage_tolerance=0.5)
    result = evaluator.evaluate(truth, prediction)

    assert result.trajectory_id == "route-1"
    assert result.matched_truth_id == "route-1"
    assert result.label_match is True
    assert result.path_error > 0
    assert result.coverage == 1.0
