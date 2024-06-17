import pytest
from swarmauri.standard.metrics.concrete.ZeroMetric import ZeroMetric

@pytest.mark.unit
def test_ubc_resource():
    def test():
        assert ZeroMetric().resource == 'Metric'
    test()

@pytest.mark.unit
def test_1():
    def test():
        assert ZeroMetric()() == 0
        assert ZeroMetric().value == 0
        assert ZeroMetric().unit == 'unitless'
    test()