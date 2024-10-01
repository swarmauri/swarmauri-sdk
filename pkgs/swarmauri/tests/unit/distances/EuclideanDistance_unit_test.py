import pytest
from swarmauri.distances.concrete.EuclideanDistance import EuclideanDistance
from swarmauri.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
    assert EuclideanDistance().resource == 'Distance'

@pytest.mark.unit
def test_ubc_type():
    assert EuclideanDistance().type == 'EuclideanDistance'

@pytest.mark.unit
def test_serialization():
    distance = EuclideanDistance()
    assert distance.id == EuclideanDistance.model_validate_json(distance.model_dump_json()).id

@pytest.mark.unit
def test_distance():
    assert EuclideanDistance().distance(
        Vector(value=[1,2]), 
        Vector(value=[1,2])
        ) == 0.0



