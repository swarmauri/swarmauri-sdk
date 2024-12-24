import pytest
from swarmauri.distances.concrete.HaversineDistance import HaversineDistance
from swarmauri.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
	assert HaversineDistance().resource == 'Distance'

@pytest.mark.unit
def test_ubc_type():
	assert HaversineDistance().type == 'HaversineDistance' 

@pytest.mark.unit
def test_serialization():
    distance = HaversineDistance() 
    assert distance.id == HaversineDistance.model_validate_json(distance.model_dump_json()).id

@pytest.mark.unit
def test_distance():
	assert HaversineDistance().distance(
	    Vector(value=[1,2]), 
	    Vector(value=[1,2])
	    ) == 0.0