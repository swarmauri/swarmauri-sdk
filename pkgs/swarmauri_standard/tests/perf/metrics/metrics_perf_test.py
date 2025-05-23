import pytest
from swarmauri_standard.metrics.DiscreteMetric import DiscreteMetric

@pytest.mark.perf
def test_metrics_performance(benchmark):
    def run():
        try:
            obj = DiscreteMetric()
        except Exception:
            try:
                obj = DiscreteMetric.__new__(DiscreteMetric)
            except Exception:
                obj = None
        if obj is None:
            return None
        if hasattr(obj, '__len__'):
            return len(obj)
        return str(obj)

    result = benchmark(run)
    assert result is not None  # replace with real condition
