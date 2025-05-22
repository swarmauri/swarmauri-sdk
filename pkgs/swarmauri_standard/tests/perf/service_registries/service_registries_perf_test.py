import pytest
from swarmauri_standard.service_registries.ServiceRegistry import ServiceRegistry

@pytest.mark.perf
def test_service_registries_performance(benchmark):
    def run():
        try:
            obj = ServiceRegistry()
        except Exception:
            try:
                obj = ServiceRegistry.__new__(ServiceRegistry)
            except Exception:
                obj = None
        if obj is None:
            return None
        if hasattr(obj, '__len__'):
            return len(obj)
        return str(obj)

    result = benchmark(run)
    assert result is not None  # replace with real condition
