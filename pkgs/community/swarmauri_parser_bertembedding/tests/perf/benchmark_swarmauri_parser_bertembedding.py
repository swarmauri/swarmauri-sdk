import pytest
from swarmauri_parser_bertembedding import BERTEmbeddingParser

@pytest.mark.perf
def test_swarmauri_parser_bertembedding_performance(benchmark):
    instance = BERTEmbeddingParser()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
