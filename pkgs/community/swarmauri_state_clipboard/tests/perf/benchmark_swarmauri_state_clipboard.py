import pytest
from swarmauri_state_clipboard import ClipboardState

@pytest.mark.perf
def test_swarmauri_state_clipboard_performance(benchmark):
    instance = ClipboardState()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
