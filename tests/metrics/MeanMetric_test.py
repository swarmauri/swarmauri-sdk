import pytest
from swarmauri.standard.metrics.concrete.MeanMetric import MeanMetric

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        assert MeanMetric(unit='average test score').resource == 'Metric'
    test()

@pytest.mark.unit
def test_1():
	def test():
		metric = MeanMetric(unit='average test score')
		metric.add_measurement(10)
		metric.add_measurement(100)
		
		assert metric() == 55.0
		assert metric.value == 55.0
		assert metric.unit == 'average test score'
	test()