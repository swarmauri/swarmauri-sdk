import pytest
from swarmauri.standard.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
	def test():
		vector = Vector(value=[1,2])
		assert vector.resource == 'Vector'
	test()



@pytest.mark.unit
def test_value_assertion():
	def test():
		vector = Vector(value=[1,2])
		assert vector.value == [1,2]
	test()

