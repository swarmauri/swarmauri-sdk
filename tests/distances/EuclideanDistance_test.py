import pytest
from swarmauri.standard.distances.concrete.EuclideanDistance import EuclideanDistance
from swarmauri.standard.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
    def test():
        assert EuclideanDistance().resource == 'Distance'
    test()

@pytest.mark.unit
def test_distance():
    def test():
        assert EuclideanDistance().distance(
            Vector(value=[1,2]), 
            Vector(value=[1,2])
            ) == 0.0
    test()



