import pytest
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
	def test():
		assert CosineDistance().resource == 'Distance'
	test()

@pytest.mark.unit
def test_distance():
	def test():
		# Floating-Point Precision Epsilon
		assert CosineDistance().distance(
			Vector(value=[1,2]), 
			Vector(value=[1,2])
			) == 2.220446049250313e-16
	test()

