import pytest
from swarmauri.standard.prompts.concrete.LevenshteinDistance import LevenshteinDistance

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        assert LevenshteinDistance().resource == 'Distance'
    test()

@pytest.mark.unit
def test_1():
    def test():
        assert LevenshteinDistance().distance(
            Vector(value=[1,2]), 
            Vector(value=[1,2])
            ) == 0.0
    test()



