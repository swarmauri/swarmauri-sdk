import pytest
from swarmauri.standard.distances.concrete.JaccardIndexDistance import JaccardIndexDistance
from swarmauri.standard.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
    def test():
        assert JaccardIndexDistance().resource == 'Distance'
    test()

@pytest.mark.unit
def test_distance():
    def test():
        assert JaccardIndexDistance().distance(
            Vector(value=[1,2]), 
            Vector(value=[1,2])
            ) == 0.0
    test()



