import pytest
from swarmauri_standard.distances.HaversineDistance import HaversineDistance
from swarmauri_standard.vectors.Vector import Vector


@pytest.mark.unit
def test_compatibility_serialization():
    distance = HaversineDistance()
    assert (
        distance.id
        == HaversineDistance.model_validate_json(distance.model_dump_json()).id
    )


@pytest.mark.unit
def test_compatibility_distance():
    assert (
        HaversineDistance().distance(Vector(value=[1, 2]), Vector(value=[1, 2])) == 0.0
    )
