import pytest
from swarmauri_parser_pypdf2 import PyPDF2Parser

@pytest.mark.perf
def test_swarmauri_parser_pypdf2_performance(benchmark):
    instance = PyPDF2Parser()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
