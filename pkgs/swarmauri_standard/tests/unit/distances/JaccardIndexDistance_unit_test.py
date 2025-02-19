import pytest
from swarmauri_standard.distances.JaccardIndexDistance import JaccardIndexDistance
from swarmauri_standard.vectors.Vector import Vector


@pytest.mark.unit
def test_ubc_resource():
    assert JaccardIndexDistance().resource == "Distance"


@pytest.mark.unit
def test_ubc_type():
    assert JaccardIndexDistance().type == "JaccardIndexDistance"


@pytest.mark.unit
def test_serialization():
    distance = JaccardIndexDistance()
    assert (
        distance.id
        == JaccardIndexDistance.model_validate_json(distance.model_dump_json()).id
    )


@pytest.mark.unit
def test_distance():
    assert (
        JaccardIndexDistance().distance(Vector(value=[1, 2]), Vector(value=[1, 2]))
        == 0.0
    )
