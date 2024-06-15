import pytest
from swarmauri.standard.metrics.concrete.StaticMetric import StaticMetric

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        assert StaticMetric(unit='jar of honey', value=10).resource == 'Metric'
    test()

@pytest.mark.unit
def test_1():
	def test():
		assert StaticMetric(unit='jar of honey', value=10)() == 10
		assert StaticMetric(unit='jar of honey', value=10).value == 10
		assert StaticMetric(unit='jar of honey', value=10).unit == 'jar of honey'
	test()