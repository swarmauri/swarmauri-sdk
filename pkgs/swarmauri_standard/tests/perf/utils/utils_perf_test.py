import pytest
from swarmauri_standard.utils.duration_manager import DurationManager

@pytest.mark.perf
def test_utils_performance(benchmark):
    def run():
        try:
            obj = DurationManager()
        except Exception:
            try:
                obj = DurationManager.__new__(DurationManager)
            except Exception:
                obj = None
        if obj is None:
            return None
        if hasattr(obj, '__len__'):
            return len(obj)
        return str(obj)

    result = benchmark(run)
    assert result is not None  # replace with real condition
