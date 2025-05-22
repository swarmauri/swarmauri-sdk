import pytest
from swarmauri_parser_slate import SlateParser

@pytest.mark.perf
def test_swarmauri_parser_slate_performance(benchmark):
    instance = SlateParser()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
