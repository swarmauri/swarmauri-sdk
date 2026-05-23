import pytest
from swarmauri_standard.distances.ChebyshevDistance import ChebyshevDistance
from swarmauri_standard.vectors.Vector import Vector


@pytest.mark.unit
def test_compatibility_serialization():
    distance = ChebyshevDistance()
    assert (
        distance.id
        == ChebyshevDistance.model_validate_json(distance.model_dump_json()).id
    )


@pytest.mark.unit
def test_compatibility_distance():
    assert (
        ChebyshevDistance().distance(Vector(value=[1, 2]), Vector(value=[1, 2])) == 0.0
    )
