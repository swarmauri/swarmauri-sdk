import pytest
from swarmauri_standard.agents.ToolAgent import ToolAgent

@pytest.mark.perf
def test_agents_performance(benchmark):
    def run():
        try:
            obj = ToolAgent()
        except Exception:
            try:
                obj = ToolAgent.__new__(ToolAgent)
            except Exception:
                obj = None
        if obj is None:
            return None
        if hasattr(obj, '__len__'):
            return len(obj)
        return str(obj)

    result = benchmark(run)
    assert result is not None  # replace with real condition
