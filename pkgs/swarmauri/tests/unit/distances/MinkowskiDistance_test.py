import pytest
from swarmauri.distances.concrete.MinkowskiDistance import MinkowskiDistance
from swarmauri.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
	assert MinkowskiDistance().resource == 'Distance'

@pytest.mark.unit
def test_ubc_type():
	assert MinkowskiDistance().type == 'MinkowskiDistance' 

@pytest.mark.unit
def test_serialization():
    distance = MinkowskiDistance() 
    assert distance.id == MinkowskiDistance.model_validate_json(distance.model_dump_json()).id

@pytest.mark.unit
def test_distance():
	assert MinkowskiDistance().distance(
	    Vector(value=[1,2]), 
	    Vector(value=[1,2])
	    ) == 0.0