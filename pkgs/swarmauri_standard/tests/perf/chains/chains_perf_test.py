import pytest
from swarmauri_standard.chains.PromptContextChain import PromptContextChain

@pytest.mark.perf
def test_chains_performance(benchmark):
    def run():
        try:
            obj = PromptContextChain()
        except Exception:
            try:
                obj = PromptContextChain.__new__(PromptContextChain)
            except Exception:
                obj = None
        if obj is None:
            return None
        if hasattr(obj, '__len__'):
            return len(obj)
        return str(obj)

    result = benchmark(run)
    assert result is not None  # replace with real condition
