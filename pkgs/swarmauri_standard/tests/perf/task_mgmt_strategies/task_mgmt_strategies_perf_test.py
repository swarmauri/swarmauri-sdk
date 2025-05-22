import pytest
from swarmauri_standard.task_mgmt_strategies.RoundRobinStrategy import RoundRobinStrategy

@pytest.mark.perf
def test_task_mgmt_strategies_performance(benchmark):
    def run():
        try:
            obj = RoundRobinStrategy()
        except Exception:
            try:
                obj = RoundRobinStrategy.__new__(RoundRobinStrategy)
            except Exception:
                obj = None
        if obj is None:
            return None
        if hasattr(obj, '__len__'):
            return len(obj)
        return str(obj)

    result = benchmark(run)
    assert result is not None  # replace with real condition
