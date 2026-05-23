import pytest
from swarmauri_standard.distances.CosineDistance import CosineDistance
from swarmauri_standard.vectors.Vector import Vector


@pytest.mark.unit
def test_compatibility_serialization():
    distance = CosineDistance()
    assert (
        distance.id == CosineDistance.model_validate_json(distance.model_dump_json()).id
    )


@pytest.mark.unit
def test_compatibility_distance():
    # Floating-Point Precision Epsilon
    assert (
        CosineDistance().distance(Vector(value=[1, 2]), Vector(value=[1, 2]))
        == 2.220446049250313e-16
    )
