import pytest
from swarmauri.standard.distances.concrete.ChebyshevDistance import ChebyshevDistance
from swarmauri.standard.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
	assert ChebyshevDistance().resource == 'Distance'

@pytest.mark.unit
def test_ubc_type():
	assert ChebyshevDistance().type == 'ChebyshevDistance' 

@pytest.mark.unit
def test_serialization():
    distance = ChebyshevDistance() 
    assert distance.id == ChebyshevDistance.model_validate_json(distance.model_dump_json()).id

@pytest.mark.unit
def test_distance():
	assert ChebyshevDistance().distance(
	    Vector(value=[1,2]), 
	    Vector(value=[1,2])
	    ) == 0.0
