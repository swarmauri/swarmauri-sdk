import pytest
from swarmauri.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
	vector = Vector(value=[1,2])
	assert vector.resource == 'Vector'

@pytest.mark.unit
def test_ubc_type():
	vector = Vector(value=[1,2])
	assert vector.type == 'Vector'

@pytest.mark.unit
def test_serialization():
	vector = Vector(value=[1,2])
	assert vector.id == Vector.model_validate_json(vector.model_dump_json()).id

@pytest.mark.unit
def test_value():
	vector = Vector(value=[1,2])
	assert vector.value == [1,2]

@pytest.mark.unit
def test_shape():
	vector = Vector(value=[1,2])
	assert vector.shape == (2,)