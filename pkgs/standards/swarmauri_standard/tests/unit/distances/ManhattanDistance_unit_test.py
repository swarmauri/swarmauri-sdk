import pytest
from swarmauri_standard.distances.ManhattanDistance import ManhattanDistance
from swarmauri_standard.vectors.Vector import Vector


@pytest.mark.unit
def test_ubc_resource():
    assert ManhattanDistance().resource == "Distance"


@pytest.mark.unit
def test_ubc_type():
    assert ManhattanDistance().type == "ManhattanDistance"


@pytest.mark.unit
def test_serialization():
    distance = ManhattanDistance()
    assert (
        distance.id
        == ManhattanDistance.model_validate_json(distance.model_dump_json()).id
    )


@pytest.mark.unit
def test_distance():
    assert (
        ManhattanDistance().distance(Vector(value=[1, 2]), Vector(value=[1, 2])) == 0.0
    )
