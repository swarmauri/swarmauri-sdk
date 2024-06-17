import pytest
from swarmauri.standard.metrics.concrete.FirstImpressionMetric import FirstImpressionMetric

@pytest.mark.unit
def test_ubc_resource():
    def test():
        assert FirstImpressionMetric(unit='points', value=10).resource == 'Metric'
    test()

@pytest.mark.unit
def test_1():
	def test():
		assert FirstImpressionMetric(unit='points', value=10)() == 10
		assert FirstImpressionMetric(unit='points', value=10).value == 10
		assert FirstImpressionMetric(unit='points', value=10).unit == 'points'
	test()