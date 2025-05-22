import pytest
from swarmauri_vectorstore_mlm import MlmVectorStore

@pytest.mark.perf
def test_swarmauri_vectorstore_mlm_performance(benchmark):
    instance = MlmVectorStore()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
