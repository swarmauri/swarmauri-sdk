import pytest
from swarmauri.standard.metrics.concrete.MeanMetric import MeanMetric as Metric

@pytest.mark.unit
def test_ubc_resource():
	assert Metric(unit='average test score').resource == 'Metric'

@pytest.mark.unit
def test_ubc_type():
    metric = Metric(unit='average test score')
    assert metric.type == 'MeanMetric'

@pytest.mark.unit
def test_serialization():
    metric = Metric(unit='points', value=10)
    assert metric.id == Metric.model_validate_json(metric.model_dump_json()).id

@pytest.mark.unit
def test_metric_value():
	metric = Metric(unit='average test score')
	metric.add_measurement(10)
	metric.add_measurement(100)

	assert metric() == 55.0
	assert metric.value == 55.0

@pytest.mark.unit
def test_metric_unit():
	metric = Metric(unit='average test score')
	metric.add_measurement(10)
	metric.add_measurement(100)
	assert metric.unit == 'average test score'