import pytest
from swarmauri_standard.distances.JaccardIndexDistance import (
    JaccardIndexDistance,
)
from swarmauri_standard.vectors.Vector import Vector


@pytest.mark.unit
def test_compatibility_serialization():
    distance = JaccardIndexDistance()
    assert (
        distance.id
        == JaccardIndexDistance.model_validate_json(
            distance.model_dump_json()
        ).id
    )


@pytest.mark.unit
def test_compatibility_distance():
    assert (
        JaccardIndexDistance().distance(
            Vector(value=[1, 2]), Vector(value=[1, 2])
        )
        == 0.0
    )
