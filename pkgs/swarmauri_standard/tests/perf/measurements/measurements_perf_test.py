import pytest
from swarmauri_standard.measurements.MiscMeasurement import MiscMeasurement

@pytest.mark.perf
def test_measurements_performance(benchmark):
    def run():
        try:
            obj = MiscMeasurement()
        except Exception:
            try:
                obj = MiscMeasurement.__new__(MiscMeasurement)
            except Exception:
                obj = None
        if obj is None:
            return None
        if hasattr(obj, '__len__'):
            return len(obj)
        return str(obj)

    result = benchmark(run)
    assert result is not None  # replace with real condition
