import pytest
from swarmauri_parser_textblob import TextBlobNounParser

@pytest.mark.perf
def test_swarmauri_parser_textblob_performance(benchmark):
    instance = TextBlobNounParser()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
