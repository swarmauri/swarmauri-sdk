import pytest
from swarmauri.standard.metrics.concrete.FirstImpressionMetric import FirstImpressionMetric as Metric

@pytest.mark.unit
def test_ubc_resource():
	assert Metric(unit='points', value=10).resource == 'Metric'


@pytest.mark.unit
def test_ubc_type():
    metric = Metric(unit='points', value=10)
    assert metric.type == 'FirstImpressionMetric'

@pytest.mark.unit
def test_serialization():
    metric = Metric(unit='points', value=10)
    assert metric.id == Metric.model_validate_json(metric.model_dump_json()).id

@pytest.mark.unit
def test_metric_value():
	assert Metric(unit='points', value=10)() == 10
	assert Metric(unit='points', value=10).value == 10


@pytest.mark.unit
def test_metric_unit():
	assert Metric(unit='points', value=10).unit == 'points'