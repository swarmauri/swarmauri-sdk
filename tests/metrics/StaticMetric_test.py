import pytest
from swarmauri.standard.metrics.concrete.StaticMetric import StaticMetric

@pytest.mark.unit
def test_ubc_resource():
    def test():
        assert StaticMetric(unit='jar of honey', value=10).resource == 'Metric'
    test()

@pytest.mark.unit
def test_metric_value():
	def test():
		assert StaticMetric(unit='jar of honey', value=10)() == 10
		assert StaticMetric(unit='jar of honey', value=10).value == 10
	test()


@pytest.mark.unit
def test_metric_unit():
	def test():
		assert StaticMetric(unit='jar of honey', value=10).unit == 'jar of honey'
	test()