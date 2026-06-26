import pytest
from swarmauri_standard.distances.ChiSquaredDistance import ChiSquaredDistance
from swarmauri_standard.vectors.Vector import Vector


@pytest.mark.unit
def test_compatibility_serialization():
    distance = ChiSquaredDistance()
    assert (
        distance.id
        == ChiSquaredDistance.model_validate_json(
            distance.model_dump_json()
        ).id
    )


@pytest.mark.unit
def test_compatibility_distance():
    assert (
        ChiSquaredDistance().distance(
            Vector(value=[1, 2]), Vector(value=[1, 2])
        )
        == 0.0
    )
