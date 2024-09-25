import pytest
from swarmauri.metrics.concrete.TokenCountEstimatorMetric import TokenCountEstimatorMetric as Metric

@pytest.mark.unit
def test_ubc_resource():
    def test():
        assert Metric().resource == 'Metric'
    test()

@pytest.mark.unit
def test_ubc_type():
    metric = Metric()
    assert metric.type == 'TokenCountEstimatorMetric'

@pytest.mark.unit
def test_serialization():
    metric = Metric()
    assert metric.id == Metric.model_validate_json(metric.model_dump_json()).id


@pytest.mark.unit
def test_metric_value():
	def test():
		assert Metric().calculate("Lorem ipsum odor amet, consectetuer adipiscing elit.") == 11
	test()


@pytest.mark.unit
def test_metric_unit():
	def test():
		assert Metric().unit == "tokens"
	test()