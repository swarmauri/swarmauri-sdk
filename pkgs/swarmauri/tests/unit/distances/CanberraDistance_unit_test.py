import pytest
from swarmauri.distances.concrete.CanberraDistance import CanberraDistance  
from swarmauri.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
	assert CanberraDistance().resource == 'Distance'

@pytest.mark.unit
def test_ubc_type():
	assert CanberraDistance().type == 'CanberraDistance' 

@pytest.mark.unit
def test_serialization():
    distance = CanberraDistance() 
    assert distance.id == CanberraDistance.model_validate_json(distance.model_dump_json()).id

@pytest.mark.unit
def test_distance():
	assert CanberraDistance().distance(
	    Vector(value=[1,2]), 
	    Vector(value=[1,2])
	    ) == 0.0
