import pytest
from swarmauri.standard.metrics.concrete.ZeroMetric import ZeroMetric as Metric

@pytest.mark.unit
def test_ubc_resource():
    assert ZeroMetric().resource == 'Metric'

@pytest.mark.unit
def test_ubc_type():
    metric = Metric(unit='points', value=10)
    assert metric.type == 'ZeroMetric'

@pytest.mark.unit
def test_serialization():
    metric = Metric(unit='points', value=10)
    assert metric.id == Metric.model_validate_json(metric.json()).id


@pytest.mark.unit
def test_metric_value():
    assert Metric()() == 0
    assert Metric().value == 0

@pytest.mark.unit
def test_metric_unit():
    assert Metric().unit == 'unitless'