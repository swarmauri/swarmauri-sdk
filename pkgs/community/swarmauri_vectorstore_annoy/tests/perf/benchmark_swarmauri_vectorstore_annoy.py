import pytest
from swarmauri_vectorstore_annoy import AnnoyVectorStore

@pytest.mark.perf
def test_swarmauri_vectorstore_annoy_performance(benchmark):
    instance = AnnoyVectorStore()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
