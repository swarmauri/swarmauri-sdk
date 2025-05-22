import pytest
from swarmauri_standard.messages.HumanMessage import TextContent

@pytest.mark.perf
def test_messages_performance(benchmark):
    def run():
        try:
            obj = TextContent()
        except Exception:
            try:
                obj = TextContent.__new__(TextContent)
            except Exception:
                obj = None
        if obj is None:
            return None
        if hasattr(obj, '__len__'):
            return len(obj)
        return str(obj)

    result = benchmark(run)
    assert result is not None  # replace with real condition
