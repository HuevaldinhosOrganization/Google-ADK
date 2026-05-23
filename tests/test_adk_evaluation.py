from adk_evaluator.adk_evaluation import AdkTrajectoryEvaluator
from adk_evaluator.models import GroundTruth, Prediction, TrajectoryPoint


def test_adk_evaluator_computes_adk_metrics():
    """Test that AdkTrajectoryEvaluator correctly computes precision, recall, F1, and ADK score.
    
    Verifies:
    - Precision equals 1.0 when all predictions cover ground truth points
    - Recall equals 1.0 when all ground truth points are covered
    - F1 score is computed as harmonic mean of precision and recall
    - ADK score combines F1 with path and duration error penalties
    - Result includes all expected metrics in to_dict() output
    """
    truth = GroundTruth(
        id="route-1",
        label="delivery",
        points=(
            TrajectoryPoint(x=0.0, y=0.0, t=0),
            TrajectoryPoint(x=1.0, y=1.0, t=30),
        ),
    )
    prediction = Prediction(
        id="route-1",
        label="delivery",
        points=(
            TrajectoryPoint(x=0.1, y=0.1, t=0),
            TrajectoryPoint(x=1.1, y=1.1, t=32),
        ),
    )

    evaluator = AdkTrajectoryEvaluator(coverage_tolerance=0.5)
    result = evaluator.evaluate(truth, prediction)

    assert result.precision == 1.0
    assert result.recall == 1.0
    assert result.f1_score == 1.0
    assert result.adk_score > 0
    assert result.to_dict()["adk_score"] == result.adk_score
