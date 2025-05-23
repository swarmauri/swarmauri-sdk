import pytest
from swarmauri_parser_pypdftk import PyPDFTKParser

@pytest.mark.perf
def test_swarmauri_parser_pypdftk_performance(benchmark):
    instance = PyPDFTKParser()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
