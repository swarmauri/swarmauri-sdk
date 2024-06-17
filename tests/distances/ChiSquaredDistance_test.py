import pytest
from swarmauri.standard.distances.concrete.ChiSquaredDistance import ChiSquaredDistance
from swarmauri.standard.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
	def test():
		assert ChiSquaredDistance().resource == 'Distance'
	test()

@pytest.mark.unit
def test_distance():
	def test():
		assert ChiSquaredDistance().distance(
		    Vector(value=[1,2]), 
		    Vector(value=[1,2])
		    ) == 0.0
	test()

