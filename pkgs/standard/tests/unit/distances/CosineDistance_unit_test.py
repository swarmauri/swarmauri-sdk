import pytest
from swarmauri.distances.concrete.CosineDistance import CosineDistance
from swarmauri.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
	assert CosineDistance().resource == 'Distance'

@pytest.mark.unit
def test_ubc_type():
	assert CosineDistance().type == 'CosineDistance'

@pytest.mark.unit
def test_serialization():
    distance = CosineDistance()
    assert distance.id == CosineDistance.model_validate_json(distance.model_dump_json()).id

@pytest.mark.unit
def test_distance():
	# Floating-Point Precision Epsilon
	assert CosineDistance().distance(
		Vector(value=[1,2]), 
		Vector(value=[1,2])
		) == 2.220446049250313e-16


