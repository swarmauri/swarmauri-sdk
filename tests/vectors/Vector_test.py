import pytest
from swarmauri.standard.vectors.concrete.Vector import Vector

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
	assert vector.id == Vector.model_validate_json(vector.model_dump()).id

@pytest.mark.unit
def test_value_assertion():
	vector = Vector(value=[1,2])
	assert vector.value == [1,2]