import pytest
from swarmauri.metrics.concrete.RatioOfSumsMetric import RatioOfSumsMetric as Metric


@pytest.mark.unit
def test_ubc_resource():
    assert Metric(value=10).resource == "Metric"


@pytest.mark.unit
def test_ubc_type():
    metric = Metric(value=10)
    assert metric.type == "RatioOfSumsMetric"

@pytest.mark.unit
def test_serialization():
    metric = Metric(value=10)
    assert metric.id == Metric.model_validate_json(metric.model_dump_json()).id


@pytest.mark.unit
def test_metric_value():
    assert Metric(value=10)() == 10


@pytest.mark.unit
def test_metric_unit():
    assert Metric(value=10).unit == "percentage"
