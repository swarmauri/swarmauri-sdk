import pytest
from swarmauri_standard.vectors.Vector import Vector

@pytest.mark.perf
def test_vectors_performance(benchmark):
    def run():
        try:
            obj = Vector()
        except Exception:
            try:
                obj = Vector.__new__(Vector)
            except Exception:
                obj = None
        if obj is None:
            return None
        if hasattr(obj, '__len__'):
            return len(obj)
        return str(obj)

    result = benchmark(run)
    assert result is not None  # replace with real condition
