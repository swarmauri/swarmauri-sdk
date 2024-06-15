import pytest
from swarmauri.standard.distances.concrete.EuclideanDistance import EuclideanDistance

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        assert EuclideanDistance().resource == 'Distance'
    test()

@pytest.mark.unit
def test_1():
    def test():
        assert EuclideanDistance().distance(
            Vector(value=[1,2]), 
            Vector(value=[1,2])
            ) == 0.0
    test()



