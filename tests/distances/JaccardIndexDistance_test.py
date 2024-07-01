import pytest
from swarmauri.standard.distances.concrete.JaccardIndexDistance import JaccardIndexDistance
from swarmauri.standard.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
    assert JaccardIndexDistance().resource == 'Distance'

@pytest.mark.unit
def test_ubc_type():
    assert JaccardIndexDistance().type == 'JaccardIndexDistance'

@pytest.mark.unit
def test_serialization():
    distance = JaccardIndexDistance()
    assert distance.id == JaccardIndexDistance.model_validate_json(distance.json()).id

@pytest.mark.unit
def test_distance():
    assert JaccardIndexDistance().distance(
        Vector(value=[1,2]), 
        Vector(value=[1,2])
        ) == 0.0



