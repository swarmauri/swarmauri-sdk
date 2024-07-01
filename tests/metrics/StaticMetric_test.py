import pytest
from swarmauri.standard.metrics.concrete.StaticMetric import StaticMetric as Metric

@pytest.mark.unit
def test_ubc_resource():
    def test():
        assert Metric(unit='jar of honey', value=10).resource == 'Metric'
    test()

@pytest.mark.unit
def test_ubc_type():
    metric = Metric(unit='points', value=10)
    assert metric.type == 'StaticMetric'

@pytest.mark.unit
def test_serialization():
    metric = Metric(unit='points', value=10)
    assert metric.id == Metric.model_validate_json(metric.json()).id


@pytest.mark.unit
def test_metric_value():
	def test():
		assert Metric(unit='jar of honey', value=10)() == 10
		assert Metric(unit='jar of honey', value=10).value == 10
	test()


@pytest.mark.unit
def test_metric_unit():
	def test():
		assert Metric(unit='jar of honey', value=10).unit == 'jar of honey'
	test()