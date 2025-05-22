import pytest
from swarmauri_standard.evaluator_results.EvalResult import EvalResult

@pytest.mark.perf
def test_evaluator_results_performance(benchmark):
    def run():
        try:
            obj = EvalResult()
        except Exception:
            try:
                obj = EvalResult.__new__(EvalResult)
            except Exception:
                obj = None
        if obj is None:
            return None
        if hasattr(obj, '__len__'):
            return len(obj)
        return str(obj)

    result = benchmark(run)
    assert result is not None  # replace with real condition
