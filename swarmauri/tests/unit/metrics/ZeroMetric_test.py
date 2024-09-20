import pytest
from swarmauri.standard.metrics.concrete.ZeroMetric import ZeroMetric as Metric

@pytest.mark.unit
def test_ubc_resource():
    assert Metric().resource == 'Metric'

@pytest.mark.unit
def test_ubc_type():
    metric = Metric()
    assert metric.type == 'ZeroMetric'

@pytest.mark.unit
def test_serialization():
    metric = Metric()
    assert metric.id == Metric.model_validate_json(metric.model_dump_json()).id


@pytest.mark.unit
def test_metric_value():
    assert Metric()() == 0
    assert Metric().value == 0

@pytest.mark.unit
def test_metric_unit():
    assert Metric().unit == 'unitless'