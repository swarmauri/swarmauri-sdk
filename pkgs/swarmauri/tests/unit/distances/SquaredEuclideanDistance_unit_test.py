import pytest
from swarmauri.distances.concrete.SquaredEuclideanDistance import SquaredEuclideanDistance
from swarmauri.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
	assert SquaredEuclideanDistance().resource == 'Distance'

@pytest.mark.unit
def test_ubc_type():
	assert SquaredEuclideanDistance().type == 'SquaredEuclideanDistance' 

@pytest.mark.unit
def test_serialization():
    distance = SquaredEuclideanDistance() 
    assert distance.id == SquaredEuclideanDistance.model_validate_json(distance.model_dump_json()).id

@pytest.mark.unit
def test_distance():
	assert SquaredEuclideanDistance().distance(
	    Vector(value=[1,2]), 
	    Vector(value=[1,2])
	    ) == 0.0