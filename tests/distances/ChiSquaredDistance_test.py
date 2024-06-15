import pytest
from swarmauri.standard.distances.concrete.ChiSquaredDistance import ChiSquaredDistance

@pytest.mark.unit
def ubc_initialization_test():
	def test():
		assert ChiSquaredDistance().resource == 'Distance'
	test()

@pytest.mark.unit
def test_1():
	def test():
		assert ChiSquaredDistance().distance(
		    Vector(value=[1,2]), 
		    Vector(value=[1,2])
		    ) == 0.0
	test()

