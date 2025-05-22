import pytest
from swarmauri_standard.programs.Program import Program

@pytest.mark.perf
def test_programs_performance(benchmark):
    def run():
        try:
            obj = Program()
        except Exception:
            try:
                obj = Program.__new__(Program)
            except Exception:
                obj = None
        if obj is None:
            return None
        if hasattr(obj, '__len__'):
            return len(obj)
        return str(obj)

    result = benchmark(run)
    assert result is not None  # replace with real condition
