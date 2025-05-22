import pytest
from swarmauri_vectorstore_qdrant import PersistentQdrantVectorStore

@pytest.mark.perf
def test_swarmauri_vectorstore_qdrant_performance(benchmark):
    instance = PersistentQdrantVectorStore()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
