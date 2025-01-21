import pytest
from swarmauri_standard.distances.SorensenDiceDistance import SorensenDiceDistance
from swarmauri_standard.vectors.Vector import Vector


@pytest.mark.unit
def test_ubc_resource():
    assert SorensenDiceDistance().resource == "Distance"


@pytest.mark.unit
def test_ubc_type():
    assert SorensenDiceDistance().type == "SorensenDiceDistance"


@pytest.mark.unit
def test_serialization():
    distance = SorensenDiceDistance()
    assert (
        distance.id
        == SorensenDiceDistance.model_validate_json(distance.model_dump_json()).id
    )


@pytest.mark.unit
def test_distance():
    assert (
        SorensenDiceDistance().distance(Vector(value=[1, 2]), Vector(value=[1, 2]))
        == 0.0
    )
