from adk_evaluator.models import Trajectory, TrajectoryPoint


def test_trajectory_serialization():
    trajectory = Trajectory(
        id="route-1",
        label="inspection",
        points=(
            TrajectoryPoint(x=0.0, y=0.0, t=0.0),
            TrajectoryPoint(x=1.0, y=1.0, t=30.0),
        ),
    )

    payload = trajectory.to_dict()
    assert payload["id"] == "route-1"
    assert payload["label"] == "inspection"
    assert len(payload["points"]) == 2

    reconstructed = Trajectory.from_dict(payload)
    assert reconstructed.id == trajectory.id
    assert reconstructed.label == trajectory.label
    assert reconstructed.point_count == trajectory.point_count
    assert reconstructed.length == trajectory.length
